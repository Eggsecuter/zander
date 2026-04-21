import copy
import math
from typing import List, Optional
from shapely import Point
from solver.debugger import Debugger
from solver.models.piece import Piece
from solver.models.solution import Solution
from solver.constants import *


class Matcher:
	def __init__(self, pieces: List[Piece]):
		self.__pieces = pieces
		self.__best_solution: Optional[Solution] = None

	def find_solution(self) -> Optional[Solution]:
		if len(self.__pieces) <= 0:
			return

		# first piece is chosen to reduce calculations (else there would be multiple identical solutions)
		for edge_index in range(len(self.__pieces[0].edges)):
			# set relative combined puzzle start point
			self.__place_next(0, edge_index, Point(0, 0), 0)

		if self.__best_solution is None:
			Debugger.log("Found no solution")
		else:
			Debugger.log(f"Found solution with score {self.__best_solution.score}\n\n")

		return self.__best_solution

	def __place_next(self, piece_index: int, edge_index: int, cursor: Point, angle_degrees: float):
		# already gone full circle
		if angle_degrees > 360:
			return

		self.__pieces[piece_index].place(edge_index, cursor, angle_degrees)

		# end reached -> evaluate solution
		if all(piece.placed_piece is not None for piece in self.__pieces):
			score = self.__score_solution()

			# potentially replace with new best solution
			if self.__best_solution is None or score < self.__best_solution.score:
				self.__best_solution = Solution(
					copy.deepcopy(self.__pieces),
					score
				)

			return

		# branch into each edge of each remaining edge
		for piece_index, piece in enumerate(self.__pieces):
			if piece.placed_piece is not None:
				continue

			for edge_index, edge in enumerate(piece.edges):
				# TODO branch into potential edges of last or already placed pieces
				# TODO correct cursor if not really 0 or 90 degree angle

				# branch into 0 degree placement
				new_cursor = self.__move_cursor(cursor, edge.length + PIECE_MARGIN_PIXEL, angle_degrees)
				self.__place_next(piece_index, edge_index, new_cursor, angle_degrees)

				# branch into 90 degree placement (for corner connections)
				new_cursor = self.__move_cursor(cursor, edge.length, angle_degrees)
				new_cursor = self.__move_cursor(cursor, PIECE_MARGIN_PIXEL, angle_degrees + 45)
				self.__place_next(piece_index, edge_index, new_cursor, angle_degrees + 90)

		# undo place after branching into every option is complete
		# this ensures cleanup when backtracking
		self.__pieces[piece_index].reset()

	def __move_cursor(self, cursor: Point, distance: float, angle_degrees: float) -> Point:
		angle_radians = math.radians(angle_degrees)

		x, y = cursor.x, cursor.y
		new_x = x + distance * math.cos(angle_radians)
		new_y = y + distance * math.sin(angle_radians)

		return Point(new_x, new_y)

	def __score_solution(self) -> float:
		# invalid if not all placed
		if any(piece.placed_piece is None for piece in self.__pieces):
			return float("inf")

		# TODO: implement real scoring logic
		return 0.0
