import time
from typing import List
from solver.logger import Logger

from solver.pipeline.contour_detector import ContourDetector

class Puzzle:
	def __init__(self, image):
		self.image = image

	def solve(self):
		if self.image is None:
			raise FileNotFoundError(f"No image loaded to solve")

		total_start_time = time.time()

		contour_start_time = time.time()
		ContourDetector.detect(self.image)
		contour_delta_time = time.time() - contour_start_time

		total_delta_time = time.time() - total_start_time

		Logger.log(f"Solved in {total_delta_time:.4f}s")
		Logger.log(f"\tContour took {contour_delta_time:.4f}s")
