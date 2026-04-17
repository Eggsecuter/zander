from typing import List

from solver.models.piece import Piece
from shapely.affinity import translate
from solver.constants import *


class CoordinateSystem:
	@staticmethod
	def correct(pieces: List[Piece]) -> List[Piece]:
		for piece in pieces:
			piece.original = translate(piece.original, A4_OFFSET_LEFT_PIXEL, A4_OFFSET_TOP_PIXEL)
			piece.edges = [translate(edge, A4_OFFSET_LEFT_PIXEL, A4_OFFSET_TOP_PIXEL) for edge in piece.edges]

		return pieces

	# TODO translate and rotate piece.placed into A5 frame
