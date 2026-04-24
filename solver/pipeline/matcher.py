import copy
import math
from typing import List, Optional
from shapely import Point
from shapely.ops import unary_union
from solver.debugger import Debugger
from solver.models.piece import Piece
from solver.models.solution import Solution
from solver.models.cursor import Cursor
import solver.constants as constants


PLACED_EDGE_START_MARGIN = 5.0
PLACED_EDGE_ANGLE_MARGIN = 5.0

class Matcher:
	def __init__(self, pieces: List[Piece]):
		self.__pieces = pieces
		self.__best_solution: Optional[Solution] = None

	def find_solution(self) -> Optional[Solution]:
		if len(self.__pieces) <= 0:
			return

		Debugger.log("Starting matching")
		self.__verbose = False
		self.__run()

		if self.__best_solution is None:
			Debugger.log("No solution found - Starting verbose matching")
			self.__verbose = True
			self.__run()

		if self.__best_solution is None:
			Debugger.log("Found no solution")
		else:
			Debugger.log(f"Found solution with score {self.__best_solution.score}\n\n")

		return self.__best_solution

	def __run(self):
		self.__optimal_option_found = False
		self.__combinations_tried = 0
		start = Cursor(Point(0, 0), 0)

		# first piece is chosen to reduce calculations (else there would be multiple identical solutions)
		for edge_index in range(len(self.__pieces[0].edges)):
			if self.__verbose or self.__pieces[0].edges[edge_index].is_frame_edge:
				# set relative combined puzzle start point
				self.__place_next(start, 0, edge_index)

		Debugger.log(f"Tried {self.__combinations_tried} combinations")

	def __place_next(self, cursor: Cursor, piece_index: int, edge_index: int):
		if self.__optimal_option_found:
			return

		# can't turn more than a full circle
		if cursor.angle_degrees > 360:
			return

		self.__combinations_tried += 1
		self.__pieces[piece_index].place(edge_index, cursor)

		# end reached -> evaluate solution
		if all(piece.placed_piece is not None for piece in self.__pieces):
			score = self.__score_solution()

			# potentially replace with new best solution
			if score < float("inf"):
				if self.__best_solution is None or score < self.__best_solution.score:
					self.__best_solution = Solution(copy.deepcopy(self.__pieces), score)

			return

		edge = self.__pieces[piece_index].placed_piece.edges[edge_index] # pyright: ignore[reportOptionalMemberAccess]
		cursor.point = Point(edge.endX, edge.endY)

		# branch into every possible cursor position
		# cursor can recursively move along already placed edges from current or other pieces
		possible_cursors: List[Cursor] = []
		possible_cursors.append(self.__move_to_piece_gap(cursor, False))
		possible_cursors.append(self.__move_to_piece_gap(cursor, True))
		possible_cursors.extend(self.__get_all_possible_cursors(cursor))

		for cursor in possible_cursors:
			# branch into each edge of each remaining edge
			for piece_index, piece in enumerate(self.__pieces):
				if piece.placed_piece is None:
					for edge_index, edge in enumerate(piece.edges):
						if self.__verbose or edge.is_frame_edge:
							self.__place_next(cursor, piece_index, edge_index)

		# undo place after branching into every option is complete
		# this ensures cleanup when backtracking
		self.__pieces[piece_index].reset()

	def __get_all_possible_cursors(self, cursor: Cursor, depth: int = 1) -> List[Cursor]:
		if depth > 10:
			return []

		possible_cursors: List[Cursor] = []

		# branch into potential edges of already placed pieces
		for piece in self.__pieces:
			if piece.placed_piece is not None:
				for edge in piece.placed_piece.edges:
					if self.__verbose or edge.is_frame_edge:
						angle_delta = abs((edge.angle_degrees - cursor.angle_degrees + 180) % 360 - 180)

						if math.hypot(cursor.point.x - edge.startX, cursor.point.y - edge.startY) <= PLACED_EDGE_START_MARGIN:
							if angle_delta <= PLACED_EDGE_ANGLE_MARGIN:
								next_cursor = Cursor(Point(edge.endX, edge.endY), cursor.angle_degrees)
								possible_cursors.extend(self.__get_all_possible_cursors(next_cursor, depth + 1))
							elif angle_delta - 90 <=PLACED_EDGE_ANGLE_MARGIN:
								next_cursor = Cursor(Point(edge.endX, edge.endY), cursor.angle_degrees + 90)
								possible_cursors.extend(self.__get_all_possible_cursors(next_cursor, depth + 1))

		return possible_cursors

	# pieces have a certain gap between each other
	# pieces can be placed in 0 or 90 degree angle (if edge is diagonal to frame corner)
	def __move_to_piece_gap(self, cursor: Cursor, angled: bool) -> Cursor:
		angle_radians = math.radians(cursor.angle_degrees + 45 if angled else 0)

		new_x = cursor.point.x + constants.PIECE_MARGIN_PIXEL * math.cos(angle_radians)
		new_y = cursor.point.y + constants.PIECE_MARGIN_PIXEL * math.sin(angle_radians)

		return Cursor(Point(new_x, new_y), cursor.angle_degrees + 90 if angled else 0)

	def __score_solution(self) -> float:
		# invalid if not all placed
		if any(piece.placed_piece is None for piece in self.__pieces):
			return float("inf")

		polygons = [piece.placed_piece.polygon for piece in self.__pieces if piece.placed_piece is not None]
		combined = unary_union(polygons)
		min_x, min_y, max_x, max_y = combined.bounds

		width = max_x - min_x
		height = max_y - min_y

		# invalid if dimensions are far off
		if max(width, height) > constants.A5_WIDTH_MICROMETER * 1.1 / constants.PIXEL_TO_MICROMETER_FACTOR:
			return float("inf")

		# get total overlap area
		sum_area = sum(polygon.area for polygon in polygons)
		overlap_area = sum_area - combined.area

		bounding_area = width * height
		size_difference = abs(bounding_area - constants.A5_AREA_PIXEL)

		score = overlap_area + size_difference

		# best option don't seek further
		if score == 0:
			self.__optimal_option_found = True

		return score
