from typing import List

import cv2
import numpy as np
from solver.models.piece import Piece
from solver.models.puzzle_frame import PuzzleFrame
from solver.models.vector_2 import Vector2


class Plotter:
	@staticmethod
	def print_info(frame: PuzzleFrame, pieces: List[Piece]):
		print('Frame: Width=' + str(frame.get_width()) + ', Height=' + str(frame.get_height()))

		for piece in pieces:
			print(str(len(piece.points)) + " - " + str(piece.center_of_mass) + " - " + str(piece.place_transform))

	@staticmethod
	def print_image(frame: PuzzleFrame, pieces: List[Piece], cursor: Vector2):
		img_height, img_width = 2600, 3200
		img = np.zeros((img_height, img_width, 3), dtype=np.uint8)

		# Draw frame
		original_contour = np.array([
			[frame.topLeft.x, frame.topLeft.y],
			[frame.topRight.x, frame.topRight.y],
			[frame.bottomRight.x, frame.bottomRight.y],
			[frame.bottomLeft.x, frame.bottomLeft.y]
		], np.int32)

		cv2.drawContours(img, [original_contour], -1, (0, 255, 255), 10)

		for i, piece in enumerate(pieces):
			placed_piece = piece.get_placed_piece()

			# Clip coordinates to image bounds
			original_contour = np.array([[int(p.x), int(p.y)] for p in piece.points], dtype=np.int32)
			placed_contour = np.array([[int(p.x), int(p.y)] for p in placed_piece.points], dtype=np.int32)

			if len(original_contour) == 0:
				continue

			original_contour = original_contour.reshape((-1, 1, 2))

			# Draw contour
			cv2.drawContours(img, [original_contour], -1, (0, 0, 255), 1)

			# Draw center of mass
			cx = max(0, min(img_width-1, int(piece.center_of_mass.x)))
			cy = max(0, min(img_height-1, int(piece.center_of_mass.y)))
			cv2.circle(img, (cx, cy), 5, (0, 0, 255), -1)

			# Optional index
			cv2.putText(img, str(i), (cx, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

			# Draw edges
			if hasattr(piece, "edges"):
				for edge in piece.edges:
					x1 = max(0, min(img_width-1, int(edge.start.x)))
					y1 = max(0, min(img_height-1, int(edge.start.y)))
					x2 = max(0, min(img_width-1, int(edge.end.x)))
					y2 = max(0, min(img_height-1, int(edge.end.y)))
					cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

			# Draw placed piece
			cv2.drawContours(img, [placed_contour], -1, (0, 255, 0), 1)

		cv2.circle(img, (int(cursor.x), int(cursor.y)), 10, (0, 0, 255), -1)

		cv2.imshow("Pieces", img)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
