from typing import List, Sequence

import cv2
from cv2.typing import MatLike
import numpy as np
from shapely import Polygon
from solver.environment import Environment
from solver.constants import *

class ContourDetector:
	@staticmethod
	def detect(image) -> List[Polygon]:
		# crop image to A4 area
		cropped_image = image[
			A4_OFFSET_TOP_PIXEL : int(A4_OFFSET_TOP_PIXEL + A4_HEIGHT_MM / PIXEL_TO_MM_FACTOR),
			A4_OFFSET_LEFT_PIXEL : int(A4_OFFSET_LEFT_PIXEL + A4_WIDTH_MM / PIXEL_TO_MM_FACTOR)
		]

		# ignore color
		grayscale_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)

		# low-pass filter to attenuate high-frequency (noise, fine textures) while preserving low-frequency (object boundaries)
		gaussian_image = cv2.GaussianBlur(grayscale_image, (5, 5), 0)

		# extract contours with different thresholds and choose best result
		# best result is where contour areas add up closest to target frame area
		# only allow results with 4 OR 6 contours
		best_score = float("inf")
		best_result: List[Polygon] = None

		target_area = ContourDetector.__get_target_area()

		for threshold in range(20, 105, 5):
			_, threshold_image = cv2.threshold(gaussian_image, threshold, 255, cv2.THRESH_BINARY_INV)
			kernel = np.ones((3,3), np.uint8)
			threshold_image = cv2.morphologyEx(threshold_image, cv2.MORPH_OPEN, kernel)
			threshold_image = cv2.morphologyEx(threshold_image, cv2.MORPH_CLOSE, kernel)

			# external to filter out holes in pieces
			contours, _ = cv2.findContours(threshold_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
			polygons = ContourDetector.__to_polygons(contours)

			score = ContourDetector.__rate_solution(polygons, target_area)

			if score < best_score:
				best_score = score
				best_result = polygons

			if Environment.log_results:
				print(f"[THRESHOLD={threshold}]\t[SCORE={score:.3f}]\tFound {len(polygons)} pieces with {[len(polygon.exterior.coords) for polygon in polygons]} points")

		if Environment.log_results:
			print(f"Best score is {best_score}")

		return best_result

	@staticmethod
	def __get_target_area() -> float:
		return A5_WIDTH_MM * A5_HEIGHT_MM / PIXEL_TO_MM_FACTOR

	@staticmethod
	def __to_polygons(contours: Sequence[MatLike]) -> List[Polygon]:
		polygons: List[Polygon] = []

		for contour in contours:
			# ignore invalid contours
			if len(contour) >= 3:
				points = contour.squeeze()

				polygon = Polygon(points)
				# roughen shape for better performance
				polygon = Polygon(polygon.simplify(0.99))

				if polygon.is_valid and polygon.area >= PIECE_MIN_AREA_PIXEL:
					polygons.append(polygon)

		return polygons

	@staticmethod
	def __rate_solution(polygons: List[Polygon], target_area: float) -> float:
		if len(polygons) == 0:
			return float("inf")

		# validate area similarity
		total_area = sum(polygon.area for polygon in polygons)
		area_error = abs(total_area - target_area) / target_area

		# validate contour count offset
		count_penalty = min(abs(len(polygons) - count) for count in PIECE_COUNTS)

		# count is a more significant fail indication
		return area_error + count_penalty * 10
