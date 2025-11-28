from solver.models.puzzle_frame import PuzzleFrame
from solver.models.piece import Piece


class PlaceUtility:
	@staticmethod
	def calculate_corner_top_left(frame: PuzzleFrame, piece: Piece):
		if len(piece.edges) != 2:
			print('Tried to place non corner piece into a corner')
			return

		# TODO calc transposition and rotation