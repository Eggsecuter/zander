from typing import Optional

from shapely.affinity import translate, scale
from solver.constants import *
from solver.models.solution import Solution


class CoordinateSystem:
	@staticmethod
	def correct(solution: Optional[Solution]):
		if solution is None:
			return

		for piece in solution.pieces:
			piece.polygon = CoordinateSystem.__correct_A4(piece.polygon)
			piece.edges = [CoordinateSystem.__correct_A4(edge) for edge in piece.edges]

			if piece.placed_piece is not None:
				piece.placed_piece.polygon = CoordinateSystem.__correct_A5(piece.placed_piece.polygon)

	@staticmethod
	def __correct_A4(geometry):
		scaled = scale(geometry, PIXEL_TO_MICROMETER_FACTOR, PIXEL_TO_MICROMETER_FACTOR, 1, (0, 0))
		return translate(scaled, A4_OFFSET_LEFT_MICROMETER, A4_OFFSET_TOP_MICROMETER)

	@staticmethod
	def __correct_A5(geometry):
		# TODO translate and rotate piece.placed into A5 frame
		scaled = scale(geometry, PIXEL_TO_MICROMETER_FACTOR, PIXEL_TO_MICROMETER_FACTOR, 1, (0, 0))
		return translate(scaled, A5_OFFSET_LEFT_MICROMETER, A5_OFFSET_TOP_MICROMETER + A5_HEIGHT_MICROMETER)
