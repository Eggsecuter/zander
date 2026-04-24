from typing import List, Sequence, cast

import cv2
from cv2.typing import MatLike
import numpy as np
from shapely import Polygon
from solver.debugger import Debugger
from solver.constants import *


ROUGHENING_TOLERANCE = 1.5

class ContourDetector:
	@staticmethod
	def detect(image) -> List[Polygon]:
		Debugger.log("Detecting contours\n")

		# crop image to A4 area
		cropped_image = image[
			A4_OFFSET_TOP_PIXEL : int(A4_OFFSET_TOP_PIXEL + A4_HEIGHT_MICROMETER / PIXEL_TO_MICROMETER_FACTOR),
			A4_OFFSET_LEFT_PIXEL : int(A4_OFFSET_LEFT_PIXEL + A4_WIDTH_MICROMETER / PIXEL_TO_MICROMETER_FACTOR)
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

		for threshold in range(20, 105, 5):
			_, threshold_image = cv2.threshold(gaussian_image, threshold, 255, cv2.THRESH_BINARY_INV)
			kernel = np.ones((3,3), np.uint8)
			threshold_image = cv2.morphologyEx(threshold_image, cv2.MORPH_OPEN, kernel)
			threshold_image = cv2.morphologyEx(threshold_image, cv2.MORPH_CLOSE, kernel)

			# external to filter out holes in pieces
			contours, _ = cv2.findContours(threshold_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
			polygons = ContourDetector.__to_polygons(contours)

			score = ContourDetector.__rate_solution(polygons, A5_AREA_PIXEL)

			if score < best_score:
				best_score = score
				best_result = polygons

			Debugger.log(f"[THRESHOLD={threshold}]\t[SCORE={score:.3f}]\tFound {len(polygons)} pieces with {[len(polygon.exterior.coords) for polygon in polygons]} points")

		Debugger.log(f"Best score is {best_score}\n\n")

		return best_result

	@staticmethod
	def __to_polygons(contours: Sequence[MatLike]) -> List[Polygon]:
		polygons: List[Polygon] = []

		for contour in contours:
			# ignore invalid contours
			if len(contour) >= 3:
				points = contour.squeeze()

				polygon = Polygon(points)
				# roughen shape for better performance
				polygon = cast(Polygon, polygon.simplify(ROUGHENING_TOLERANCE, preserve_topology=True))

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

		# validate contour noise
		vertex_penalty = sum(len(polygon.exterior.coords) for polygon in polygons) / len(polygons)
		compactness_penalty = sum((polygon.length / polygon.area) for polygon in polygons if polygon.area > 0) / len(polygons)
		convexity_penalty = sum(((p.convex_hull.area - p.area) / p.convex_hull.area) for p in polygons if p.convex_hull.area > 0) / len(polygons)

		return (
			area_error
			+ vertex_penalty * 0.01
			+ compactness_penalty * 0.1
			+ convexity_penalty * 2
			+ count_penalty * 10
		)
