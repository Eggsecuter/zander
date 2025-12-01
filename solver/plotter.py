from typing import List

import cv2
import numpy as np
from solver.models.piece import Piece
from solver.models.placed_piece import PlacedPiece
from solver.models.puzzle_frame import PuzzleFrame
from solver.models.vector2 import Vector2


class Plotter:
	@staticmethod
	def print_info(frame: PuzzleFrame, pieces: List[Piece]):
		print('Frame: Width=' + str(frame.get_width()) + ', Height=' + str(frame.get_height()))

		for piece in pieces:
			print(str(len(piece.points)) + " - " + str(piece.center_of_mass) + " - " + str(piece.place_transform))

	@staticmethod
	def print_image(image, frame: PuzzleFrame, pieces: List[Piece], cursor: Vector2):
		img_height, img_width = image.shape[:2]

		img = np.zeros((img_height, img_width, 3), dtype=np.uint8)

		# Helper to convert percentile -> pixel coordinates (0–100 → image size)
		def scale(vector: Vector2):
			longer_dimension = img_width if img_width > img_height else img_height

			x = int(vector.x / 100 * longer_dimension)
			y = int(vector.y / 100 * longer_dimension)

			return x, image.shape[0] - y

		# Draw frame
		frame_contour = np.array([
			scale(frame.topLeft),
			scale(frame.topRight),
			scale(frame.bottomRight),
			scale(frame.bottomLeft)
		], np.int32)
		cv2.drawContours(img, [frame_contour], -1, (0, 255, 255), 2)

		for i, piece in enumerate(pieces):
			placed_piece = PlacedPiece.get_from(piece)

			if len(piece.points) == 0:
				continue

			# Scale contours for drawing
			original_contour = np.array([scale(p) for p in piece.points], np.int32).reshape((-1, 1, 2))
			placed_contour = np.array([scale(p) for p in placed_piece.points], np.int32).reshape((-1, 1, 2))

			# Draw original piece
			cv2.drawContours(img, [original_contour], -1, (0, 0, 255), 1)

			for point in piece.points:
				cv2.circle(img, (scale(point)), 5, (0, 0, 255), -1)

			# Draw center of mass
			cx, cy = scale(piece.center_of_mass)
			cv2.circle(img, (cx, cy), 5, (0, 0, 255), -1)
			cv2.putText(img, str(i), (cx, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

			# Draw edges
			if hasattr(piece, "edges"):
				for edge in piece.edges:
					x1, y1 = scale(edge.start)
					x2, y2 = scale(edge.end)
					cv2.arrowedLine(img, (x1, y1), (x2, y2), (255, 0, 0), 2, tipLength=0.1)

			# Draw placed piece
			# cv2.drawContours(img, [placed_contour], -1, (0, 255, 0), 1)
			# pcx, pcy = scale(placed_piece.center_of_mass)
			# cv2.circle(img, (pcx, pcy), 5, (0, 255, 0), -1)

			# Draw placed piece edges
			# if hasattr(piece, "edges"):
			# 	for index, edge in enumerate(placed_piece.edges):
			# 		x1, y1 = scale(edge.start)
			# 		x2, y2 = scale(edge.end)
			# 		cv2.arrowedLine(img, (x1, y1), (x2, y2), (150, 0, 150), 2, tipLength=0.1)

		# Draw cursor
		cx, cy = scale(cursor)
		cv2.circle(img, (cx, cy), 10, (0, 0, 255), -1)

		cv2.imshow("Pieces", img)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
