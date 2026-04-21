import time
import cv2
from typing import Optional

from solver.debugger import Debugger
from solver.models.solution import Solution
from solver.pipeline.contour_detector import ContourDetector
from solver.pipeline.coordinate_system import CoordinateSystem
from solver.pipeline.matcher import Matcher
from solver.pipeline.piece_detector import PieceDetector


class Puzzle:
	@staticmethod
	def solve(image) -> Optional[Solution]:
		if image is None:
			raise FileNotFoundError("No image loaded to solve")

		# for easier coordination rotate image by 180 degrees
		image = cv2.flip(image, -1)

		total_start_time = time.time()

		contour_start_time = time.time()
		polygons = ContourDetector.detect(image)
		contour_delta_time = time.time() - contour_start_time

		match_start_time = time.time()
		pieces = PieceDetector.detect(polygons)
		piece_delta_time = time.time() - match_start_time

		match_start_time = time.time()
		solution = Matcher(pieces).find_solution()
		match_delta_time = time.time() - match_start_time

		coordinate_start_time = time.time()
		CoordinateSystem.correct(solution)
		coordinate_delta_time = time.time() - coordinate_start_time

		total_delta_time = time.time() - total_start_time

		Debugger.log(f"Solved in {total_delta_time:.4f}s")
		Debugger.log(f"\tContour detector took {contour_delta_time:.4f}s")
		Debugger.log(f"\tPiece detector took {piece_delta_time:.4f}s")
		Debugger.log(f"\tMatcher took {match_delta_time:.4f}s")
		Debugger.log(f"\tCoordinate took {coordinate_delta_time:.4f}s")

		Debugger.plot(image, [] if solution is None else solution.pieces)

		return solution
