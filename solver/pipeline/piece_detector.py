import cv2
import numpy as np

from typing import List, Tuple
from solver.models.piece import Piece
from solver.models.vector2 import Vector2
from solver.utility.polygon import PolygonUtility

ROUGHENING_EPSILON: float = 0.05
EDGE_LINE_EPSILON: float = 0.1
EDGE_MIN_LENGTH: float = 3.0 # TODO lower
EDGE_CORNER_MARGIN: float = 1.0
EDGE_CORNER_MARGIN_DEGREES: float = 10.0

class PieceDetector:
	@staticmethod
	def detect(image) -> List[Piece]:
		pieces: List[Piece] = []
		contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

		for contour in contours:
			coordinates = contour.reshape(-1, 2)
			vectors = [PieceDetector.normalize_coordinate(image, coordinate[0], coordinate[1]) for coordinate in coordinates]

			# TODO disregard points out of bounding box (crop camera image to A4 place)
			# TODO account for puzzle height (homography)
			points = PolygonUtility.roughen(vectors, ROUGHENING_EPSILON)
			center_of_mass = PolygonUtility.calculate_center_of_mass(points)
			edges = PolygonUtility.detect_edges(points, EDGE_LINE_EPSILON, EDGE_MIN_LENGTH, EDGE_CORNER_MARGIN, EDGE_CORNER_MARGIN_DEGREES)

			piece = Piece(points, center_of_mass, edges)
			pieces.append(piece)

		return pieces

	@staticmethod
	def normalize_coordinate(image, x: float, y: float):
		'''
		Normalizes into percentile coordinate system with its origin point at the bottom left.
		This allows intuitive radiant angles and also unified margin values for further matching and solving of the puzzle.

		Because the margin (for transposition and rotation) are absolute differently sized images would need different margin values, which gets prevented by normalizing the vectors
		'''
		img_height, img_width = image.shape[:2]

		# open cv has its origin point at the top left corner
		# simplify further calculations by having the origin in the bottom left
		y = img_height - y

		# solver calculates with percentile coordinates to be compatible with any further robotic coordinate system
		# take the longer dimension to prevent stretching
		longer_dimension = img_width if img_width > img_height else img_height
		x *= 100 / longer_dimension
		y *= 100 / longer_dimension

		return Vector2(float(x), float(y))
