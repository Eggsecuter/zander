import math
from typing import List

from solver.models.edge import Edge
from solver.models.piece import Piece
from solver.models.place_transform import PlaceTransform
from solver.models.puzzle_frame import PuzzleFrame, FrameSide
from solver.models.vector_2 import Vector2

class Matcher:
	def __init__(self, frame: PuzzleFrame, pieces: List[Piece]):
		self.frame = frame
		self.pieces = pieces

		# used for orientation during solving
		self.current_edge_direction: float = math.pi * 0
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

		for edge in root_piece.edges:
			# align edge to current direction
			root_piece.place_transform.rotation_radiant = self.__rotation_needed(edge, self.current_edge_direction)

			# solution_found = Matcher.__place_next(rootPiece, pieces.copy()[1:])

			# if solution_found:
			# 	break

	def __place_next(self, root: Piece, remaining_pieces: List[Piece]) -> bool:
		for piece in remaining_pieces:
			for edge in piece.edges:
				# TODO rotate and transpose to align
				place_transform = PlaceTransform(Vector2(0, 0), 0)

				if not Matcher.__is_matching(root, piece):
					continue

				piece.place_transform = place_transform

				# last piece places successfully
				if len(remaining_pieces) == 1:
					return True

				new_remaining = remaining_pieces.copy()
				new_remaining.remove(piece)
				solution_found = Matcher.__place_next(piece, new_remaining)

				if solution_found:
					# TODO check if overflows frame dimensions
					return True

		return False

	def __is_matching(self, root: Piece, target: Piece) -> bool:
		# TODO algo
		return True

	def __slide_along_corners(self):
		pass

	def __is_valid_turn(self, turn: Vector2) -> bool:
		# TODO measure distance between turns
		# TODO if not any valid length (frame width or height) -> false
		# TODO if length is equal to last length -> false

		return True

	def __rotation_needed(self, edge: Edge, target: float) -> float:
		delta = target - edge.get_angle()
		delta = (delta + math.pi) % (2 * math.pi) - math.pi

		return delta
