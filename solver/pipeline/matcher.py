import copy
import math
from typing import List

from solver.models.edge import Edge
from solver.models.piece import Piece
from solver.models.place_transform import PlaceTransform
from solver.models.puzzle_frame import PuzzleFrame, FrameSide
from solver.models.vector_2 import Vector2

# TODO GENERALLY -> currently slide along edges is okay. but it has to be extended that it accounts previous edges as well meaning: if it has a previous connecting edge the orientation is invalid (because left to right)

PUZZLE_PIECE_MARGIN = 10 # TODO after implementing (absolute robot coordinates: see solver/shape_detector.py) define real world margin

class Matcher:
	def __init__(self, frame: PuzzleFrame, pieces: List[Piece]):
		self.frame = frame
		self.pieces = pieces

		# used for orientation during solving
		self.current_direction: float = 0
		self.cursor: Vector2 = Vector2(0, 0) # current position for edge matching
		self.last_turn: Vector2 = None
		self.last_completed_side: FrameSide = None

	def solve(self):
		'''
		This algorithm solves the puzzle and places it into the frame. For the final solution each piece received their place transform.

		It starts by taking the piece with the least amount of frame edges (place possibilities) and appending place the remaining pieces along the frame edges until none are left.
		'''
		if len(self.pieces) <= 0:
			print('No pieces')
			return

		# start with placing the first piece
		self.pieces.sort(key=lambda piece: len(piece.edges), reverse=True)
		root_piece = self.pieces[0]

		for edge_index in range(len(root_piece.edges)):
			# align edge to current direction
			root_piece.place_transform.rotation_radiant = self.__rotation_needed(root_piece.edges[edge_index])

			# TODO temp
			root_piece.place_transform.position = Vector2(1500, 1800)

			place_root_piece = root_piece.get_placed_piece()

			solution_found = self.__place_next(place_root_piece, edge_index, self.pieces.copy()[1:])

			if solution_found:
				print('solution found')
				break

	def __place_next(self, last_placed_piece: Piece, last_edge_index: int, remaining_pieces: List[Piece]) -> bool:
		# slides the cursor along the connecting edges and checks if the piece takes a turn too early
		is_long_enough = self.__slide_along_frame_edges(last_placed_piece, last_edge_index)

		if not is_long_enough:
			return False

		if len(remaining_pieces) == 0:
			return True

		# TODO temp
		if len(remaining_pieces) == 3:
			return True

		for piece in remaining_pieces:
			for edge_index, edge in enumerate(piece.edges):
				self.__calculate_place_transform(piece, edge_index)
				placed_piece = piece.get_placed_piece()

				if self.__is_overflowing_frame(placed_piece.edges[edge_index]):
					continue

				if not self.__is_matching(last_placed_piece, piece):
					continue

				new_remaining = remaining_pieces.copy()
				new_remaining.remove(piece)
				solution_found = self.__place_next(placed_piece, edge_index, new_remaining)

				if solution_found:
					return True

		return False

	def __rotation_needed(self, edge: Edge) -> float:
		delta = self.current_direction - edge.get_angle()
		delta = (delta + math.pi) % (2 * math.pi) - math.pi

		return delta

	def __slide_along_frame_edges(self, piece: Piece, last_edge_index: int, margin=100.0, angle_tolerance=0.01) -> bool:
		old_cursor = self.cursor
		self.cursor = copy.deepcopy(piece.edges[last_edge_index].end)

		while True:
			connecting_edge: Edge = None

			for edge in piece.edges:
				if edge.start.distance_to(self.cursor) <= margin:
					if math.isclose(edge.get_angle(), self.__get_next_direction(), abs_tol=angle_tolerance):
						connecting_edge = edge
						break

			if connecting_edge is None:
				break

			if self.__is_valid_turn(connecting_edge):
				self.current_direction = self.__get_next_direction()
				self.cursor = self.__get_next_cursor_point(connecting_edge)
			else:
				# invalid puzzle edge on puzzle piece, would turn too soon and won't fill out frame
				self.cursor = old_cursor
				return False

		return True

	def __is_overflowing_frame(self, edge: Edge, margin=1e-3) -> bool:
		if self.last_turn is None:
			return False

		current_frame_side_length: float

		if self.last_completed_side is None or self.last_completed_side == FrameSide.WIDTH:
			current_frame_side_length = self.frame.get_height()
		else:
			current_frame_side_length = self.frame.get_width()

		# edge should not overflow frame
		return edge.end.distance_to(self.last_turn) > current_frame_side_length + margin

	def __is_valid_turn(self, edge: Edge, margin=1e-3) -> bool:
		# take start of turning edge to measure side length
		turn_point = edge.start

		if self.last_completed_side is None and self.last_turn is None:
			self.last_turn = turn_point
			return True

		distance_between_turns = self.last_turn.distance_to(turn_point)
		current_frame_side: FrameSide = None

		if math.isclose(distance_between_turns, self.frame.get_height(), abs_tol=margin):
			current_frame_side = FrameSide.HEIGHT
		elif math.isclose(distance_between_turns, self.frame.get_width(), abs_tol=margin):
			current_frame_side = FrameSide.WIDTH

		if current_frame_side is not None and (self.last_completed_side is None or self.last_completed_side != current_frame_side):
			self.last_completed_side = current_frame_side
			return True
		else:
			# can't have two of the same frame sides consecutively, they always alternate
			return False

	def __get_next_direction(self) -> float:
		# rotate counter clockwise
		# only 90 degree turns are allowed
		return (self.current_direction + math.pi / 2) % (2 * math.pi)

	def __get_next_cursor_point(self, edge: Edge):
		# add half the margin to reduce robotic placement issues
		move_amount = PUZZLE_PIECE_MARGIN / 2

		return Vector2(
			edge.end.x + move_amount * math.cos(self.current_direction),
			edge.end.y + move_amount * math.sin(self.current_direction)
		)








	def __is_matching(self, root: Piece, target: Piece) -> bool:
		# TODO algo
		return True






	# TODO cleanup
	def __calculate_place_transform(self, piece: Piece, edge_index: int) -> PlaceTransform:
		"""
		Returns a PlaceTransform that moves & rotates the piece so that:
		- piece.edges[edge_index].start == self.cursor
		- piece.edges[edge_index] is pointing along self.current_direction
		"""

		# --- 1) Compute rotation needed ---
		first_edge = piece.edges[edge_index]
		dx = first_edge.end.x - first_edge.start.x
		dy = first_edge.end.y - first_edge.start.y
		current_angle = math.atan2(dy, dx)

		# rotation needed to align with current_direction
		rotation_radiant = self.current_direction - current_angle

		# --- 2) Compute new center of mass after rotation ---
		# rotate vector from center_of_mass to first_edge.start
		cx, cy = piece.center_of_mass.x, piece.center_of_mass.y
		sx, sy = first_edge.start.x, first_edge.start.y

		# vector from center to start of edge
		vx = sx - cx
		vy = sy - cy

		cos_r = math.cos(rotation_radiant)
		sin_r = math.sin(rotation_radiant)

		# rotated vector
		rx = vx * cos_r - vy * sin_r
		ry = vx * sin_r + vy * cos_r

		# new center so that first edge start matches cursor
		new_center_x = self.cursor.x - rx
		new_center_y = self.cursor.y - ry
		position = Vector2(new_center_x, new_center_y)

		piece.place_transform.position = position
		piece.place_transform.rotation_radiant = rotation_radiant
