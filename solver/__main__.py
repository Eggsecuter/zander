import cv2
import numpy as np

from typing import List
from solver.example.buffer_example import buffer
from solver.models.puzzle_frame import PuzzleFrame
from solver.pipeline.matcher import Matcher
from solver.pipeline.shape_detector import ShapeDetector
from solver.pipeline.image_loader import ImageLoader
from solver.models.piece import Piece
from solver.pipeline.piece_detector import PieceDetector

class Main:
	# overview of fields
	def __init__(self):
		self.image = None
		self.frame: PuzzleFrame = None
		self.pieces: List[Piece] = None

	def load_image_from_buffer(self, image_buffer: bytearray):
		self.image = ImageLoader.from_buffer(image_buffer)

	def load_image_from_path(self, image_path: str):
		self.image = ImageLoader.from_path(image_path)

	def run(self):
		if (self.image is None):
			print('No image loaded!')
			return

		self.image = ShapeDetector.detect(self.image)
		self.frame, self.pieces = PieceDetector.detect(self.image)

		# Matcher.solve(..., self.pieces)

		print(self.frame)

		for piece in self.pieces:
			print(str(len(piece.points)) + " - " + str(piece.center_of_mass) + " - " + str(piece.place_transform))

		self.print_image()

	def print_image(self):
		img_height, img_width = 2600, 3200
		img = np.zeros((img_height, img_width, 3), dtype=np.uint8)

		# Draw frame
		contour = np.array([
			[self.frame.topLeft.x, self.frame.topLeft.y],
			[self.frame.topRight.x, self.frame.topRight.y],
			[self.frame.bottomRight.x, self.frame.bottomRight.y],
			[self.frame.bottomLeft.x, self.frame.bottomLeft.y]
		], np.int32)

		cv2.drawContours(img, [contour], -1, (0, 255, 255), 10)

		for i, piece in enumerate(self.pieces):
			# Clip coordinates to image bounds
			contour = np.array([[max(0, min(img_width-1, int(p.x))),
								max(0, min(img_height-1, int(p.y)))] for p in piece.points], dtype=np.int32)
			if len(contour) == 0:
				continue
			contour = contour.reshape((-1, 1, 2))

			# Draw contour
			cv2.drawContours(img, [contour], -1, (0, 0, 255), 1)

			# Draw center of mass
			cx = max(0, min(img_width-1, int(piece.center_of_mass.x)))
			cy = max(0, min(img_height-1, int(piece.center_of_mass.y)))
			cv2.circle(img, (cx, cy), 5, (0, 255, 0), -1)

			# Optional index
			cv2.putText(img, str(i), (cx, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

			# --- Draw edges in green ---
			if hasattr(piece, "edges"):
				for edge in piece.edges:
					x1 = max(0, min(img_width-1, int(edge.start.x)))
					y1 = max(0, min(img_height-1, int(edge.start.y)))
					x2 = max(0, min(img_width-1, int(edge.end.x)))
					y2 = max(0, min(img_height-1, int(edge.end.y)))
					cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

		cv2.imshow("Pieces", img)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

if __name__ == "__main__":
	main = Main()

	# TODO try over and over again with different margin values (for each method in the whole algorithm) until it finds an optimal solution
	main.load_image_from_buffer(buffer)
	# main.load_image_from_path('./data/image-005.png')
	main.run()
