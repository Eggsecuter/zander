import time
from typing import List
from solver.debugger import Debugger

from solver.models.piece import Piece
from solver.pipeline.contour_detector import ContourDetector
from solver.pipeline.coordinate_system import CoordinateSystem
from solver.pipeline.matcher import Matcher
from solver.pipeline.piece_detector import PieceDetector


class Puzzle:
	@staticmethod
	def solve(image) -> List[Piece]:
		if image is None:
			raise FileNotFoundError(f"No image loaded to solve")

		total_start_time = time.time()

		contour_start_time = time.time()
		polygons = ContourDetector.detect(image)
		contour_delta_time = time.time() - contour_start_time

		match_start_time = time.time()
		pieces = PieceDetector.detect(polygons)
		piece_delta_time = time.time() - match_start_time

		match_start_time = time.time()
		pieces = Matcher.match(pieces)
		match_delta_time = time.time() - match_start_time

		coordinate_start_time = time.time()
		pieces = CoordinateSystem.correct(pieces)
		coordinate_delta_time = time.time() - coordinate_start_time

		total_delta_time = time.time() - total_start_time

		Debugger.log(f"Solved in {total_delta_time:.4f}s")
		Debugger.log(f"\tContour detector took {contour_delta_time:.4f}s")
		Debugger.log(f"\tPiece detector took {piece_delta_time:.4f}s")
		Debugger.log(f"\tMatcher took {match_delta_time:.4f}s")
		Debugger.log(f"\tCoordinate took {coordinate_delta_time:.4f}s")

		Debugger.plot(image, pieces)

		return pieces
