import cv2
import numpy as np

from typing import List, Tuple
from solver.models.piece import Piece
from solver.models.puzzle_frame import PuzzleFrame
from solver.models.vector_2 import Vector2
from solver.utility.polygon import PolygonUtility

FRAME_WIDTH_PERCENTAGE = 30

class PieceDetector:
	@staticmethod
	def detect(image) -> Tuple[PuzzleFrame, List[Piece]]:
		contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

		frame: PuzzleFrame = None
		pieces: List[Piece] = []

		for contour in contours:
			coordinates = contour.reshape(-1, 2)
			vectors = [PieceDetector.normalize_coordinate(image, coordinate[0], coordinate[1]) for coordinate in coordinates]

			# frame
			if any(vector.x < FRAME_WIDTH_PERCENTAGE for vector in vectors):
				frame = PieceDetector.get_frame(vectors)
			# piece
			else:
				piece = Piece(vectors)
				pieces.append(piece)

		return frame, pieces

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

	@staticmethod
	def get_frame(points: List[Vector2]) -> PuzzleFrame:
		points = np.array([[p.x, p.y] for p in points], dtype=np.float32)

		rectangle = cv2.minAreaRect(points)
		box = cv2.boxPoints(rectangle)

		s = box.sum(axis=1)
		diff = np.diff(box, axis=1)

		topLeft = box[np.argmin(s)]
		bottomRight = box[np.argmax(s)]
		topRight = box[np.argmin(diff)]
		bottomLeft = box[np.argmax(diff)]

		return PuzzleFrame(
			topLeft=Vector2(float(topLeft[0]), float(topLeft[1])),
			topRight=Vector2(float(topRight[0]), float(topRight[1])),
			bottomRight=Vector2(float(bottomRight[0]), float(bottomRight[1])),
			bottomLeft=Vector2(float(bottomLeft[0]), float(bottomLeft[1]))
		)
