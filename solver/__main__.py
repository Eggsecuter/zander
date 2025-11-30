import time

from typing import List
from solver.example.buffer_example import buffer
from solver.models.puzzle_frame import PuzzleFrame
from solver.pipeline.matcher import Matcher
from solver.pipeline.shape_detector import ShapeDetector
from solver.pipeline.image_loader import ImageLoader
from solver.models.piece import Piece
from solver.pipeline.piece_detector import PieceDetector
from solver.plotter import Plotter

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

		start_time = time.time()
		matcher = Matcher(self.frame, self.pieces)
		matcher.solve()

		delta_time = time.time() - start_time
		print(f"Matching processed in: {delta_time:.4f} seconds")

		# TODO instead return instructions for server
		Plotter.print_info(self.frame, self.pieces)
		Plotter.print_image(self.image, self.frame, self.pieces, matcher.cursor)

if __name__ == "__main__":
	main = Main()

	# TODO try over and over again with different margin values (for each method in the whole algorithm) until it finds an optimal solution
	main.load_image_from_buffer(buffer)
	main.run()
