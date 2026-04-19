from typing import List

from solver.models.piece import Piece
from shapely.affinity import translate, scale
from solver.constants import *


class CoordinateSystem:
	@staticmethod
	def correct(pieces: List[Piece]) -> List[Piece]:
		for piece in pieces:
			piece.polygon = CoordinateSystem.__correct_A4(piece.polygon)
			piece.edges = [CoordinateSystem.__correct_A4(edge) for edge in piece.edges]
			piece.placed_piece.polygon = CoordinateSystem.__correct_A5(piece.polygon)

		return pieces

	@staticmethod
	def __correct_A4(geometry):
		scaled = scale(geometry, PIXEL_TO_MICROMETER_FACTOR, PIXEL_TO_MICROMETER_FACTOR, 1, (0, 0))
		return translate(scaled, A4_OFFSET_LEFT_MICROMETER, A4_OFFSET_TOP_MICROMETER)

	@staticmethod
	def __correct_A5(geometry):
		# TODO translate and rotate piece.placed into A5 frame

		return translate(geometry, A5_OFFSET_LEFT_MICROMETER, A5_OFFSET_TOP_MICROMETER)
