import copy
import math
from typing import List

from solver.models.edge import Edge
from solver.models.frame_side import FrameSide
from solver.models.piece import Piece
from solver.models.place_transform import PlaceTransform
from solver.models.placed_piece import PlacedPiece
from solver.models.puzzle_frame import PuzzleFrame
from solver.models.vector2 import Vector2
from solver.plotter import Plotter
from solver.utility.polygon import PolygonUtility

# TODO define real world margin
PUZZLE_PIECE_MARGIN = 1.0
FULL_CIRCLE_MARGIN = 1.0

class Matcher:
	@property
	def current_cursor(self) -> Vector2:
		return self.cursor_history[-1]

	@property
	def current_direction(self) -> float:
		return self.direction_history[-1]

	def __init__(self, frame: PuzzleFrame, pieces: List[Piece]):
		self.frame = frame
		self.pieces = pieces

		# used for orientation during solving
		self.cursor_history: List[Vector2] = []
		self.direction_history: List[float] = []

		# debugger
		self.place_count = 0

	def solve(self):
		'''
		This algorithm solves the puzzle and places it into the frame. For the final solution each piece received their place transform.

		It starts by taking the piece with the least amount of frame edges (place possibilities) and appending place the remaining pieces along the frame edges until none are left.
		'''
		if len(self.pieces) <= 0:
			print('No pieces')
			return

		# place first piece relatively
		self.pieces.sort(key=lambda piece: len(piece.edges), reverse=True)
		root_piece = self.pieces[0]

		for edge_index in range(len(root_piece.edges)):
			# align edge to current direction
			delta = -root_piece.edges[edge_index].get_end_angle()
			root_piece.place_transform.rotation_radiant = (delta + math.pi) % (2 * math.pi) - math.pi
			root_piece.place_transform.position = Vector2(25, 10)

			placed_root_piece = PlacedPiece.get_from(root_piece)
			self.cursor_history.append(placed_root_piece.edges[edge_index].start.copy())
			self.direction_history.append(0)
			self.cursor_history.append(placed_root_piece.edges[edge_index].end.copy())

			solved = self.__place_next(placed_root_piece, self.pieces[1:])

			if solved:
				self.__transform_into_frame()
				print(f'Solution found in {self.place_count} steps')
				break

	def __place_next(self, previous: PlacedPiece, remaining_pieces: List[Piece]) -> bool:
		if len(remaining_pieces) == 0:
			if abs(self.current_cursor.distance_to(self.cursor_history[0])) <= FULL_CIRCLE_MARGIN:
				return True

			return False

		for piece in remaining_pieces:
			for edge_index in range(len(piece.edges)):
				self.place_count += 1

				self.__calculate_place_transform(piece, piece.edges[edge_index])
				placed_piece = PlacedPiece.get_from(piece)

				# TODO check contours

				self.__update_placement_orientation(placed_piece.edges[edge_index])

				new_remaining = remaining_pieces.copy()
				new_remaining.remove(piece)
				solved = self.__place_next(placed_piece, new_remaining)

				if solved:
					return True
				else:
					self.cursor_history.pop()
					self.direction_history.pop()

		return False

	def __update_placement_orientation(self, edge: Edge) -> bool:
		new_direction = self.current_direction + (math.pi / 2) * edge.corner_count
		new_direction = (new_direction + math.pi) % (2 * math.pi) - math.pi
		self.direction_history.append(new_direction)

		# add half the margin to reduce robotic placement issues
		move_amount = PUZZLE_PIECE_MARGIN / 2

		self.cursor_history.append(Vector2(
			edge.end.x + move_amount * math.cos(self.current_direction),
			edge.end.y + move_amount * math.sin(self.current_direction)
		))

	def __calculate_place_transform(self, piece: Piece, edge: Edge) -> PlaceTransform:
		"""
		Returns a PlaceTransform that moves & rotates the piece so that:
		- edge.start == self.current_cursor
		- edge is pointing along self.current_direction
		"""
		# rotation needed to align with current_direction
		rotation_radiant = self.current_direction - edge.get_start_angle()

		# --- 2) Compute new center of mass after rotation ---
		# rotate vector from center_of_mass to first_edge.start
		cx, cy = piece.center_of_mass.x, piece.center_of_mass.y
		sx, sy = edge.start.x, edge.start.y

		# vector from center to start of edge
		vx = sx - cx
		vy = sy - cy

		cos_r = math.cos(rotation_radiant)
		sin_r = math.sin(rotation_radiant)

		# rotated vector
		rx = vx * cos_r - vy * sin_r
		ry = vx * sin_r + vy * cos_r

		# new center so that first edge start matches cursor
		new_center_x = self.current_cursor.x - rx
		new_center_y = self.current_cursor.y - ry
		position = Vector2(new_center_x, new_center_y)

		piece.place_transform.position = position
		piece.place_transform.rotation_radiant = rotation_radiant

	def __transform_into_frame(self):
		# cursor history forms frame
		relative_frame_center_of_mass = PolygonUtility.calculate_center_of_mass(self.cursor_history)

		frame_center_of_mass = Vector2(
			self.frame.bottomLeft.x + self.frame.get_width() / 2,
			self.frame.bottomLeft.y + self.frame.get_height() / 2
		)

		translation = frame_center_of_mass - relative_frame_center_of_mass

		for piece in self.pieces:
			piece.place_transform.position += translation
