import copy
from typing import List
from solver.models.piece import Piece


class Matcher:
	@staticmethod
	def match(pieces: List[Piece]) -> List[Piece]:
		for piece in pieces:
			copied_piece = copy.deepcopy(piece.original)
			piece.place(copied_piece)

		return pieces
