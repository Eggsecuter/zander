from typing import List

from solver.models.piece import Piece
from shapely.affinity import translate
from solver.constants import *


class CoordinateSystem:
	@staticmethod
	def correct(pieces: List[Piece]) -> List[Piece]:
		for piece in pieces:
			piece.polygon = CoordinateSystem.__correct_A4(piece.polygon)
			piece.edges = [CoordinateSystem.__correct_A4(edge) for edge in piece.edges]

		return pieces

	@staticmethod
	def __correct_A4(geometry):
		return translate(geometry, A4_OFFSET_LEFT_PIXEL, A4_OFFSET_TOP_PIXEL)

	@staticmethod
	def __correct_A5(geometry):
		# TODO translate and rotate piece.placed into A5 frame
		pass
