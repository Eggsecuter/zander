from typing import List
from shapely.geometry import box
from solver.models.piece import Piece
from solver.plot import Plot
from solver.constants import *


class Debugger:
	__log_enabled: bool = False
	__plot_enabled: bool = False

	@staticmethod
	def enable_log():
		Debugger.__log_enabled = True

	@staticmethod
	def enable_plot():
		Debugger.__plot_enabled = True

	@staticmethod
	def log(message):
		if not Debugger.__log_enabled:
			return

		print(message)

	@staticmethod
	def plot(image, pieces: List[Piece]):
		if not Debugger.__plot_enabled:
			return

		solved_color=(0, 150, 255)

		plot = Plot()
		plot.add_image(image, PIXEL_TO_MICROMETER_FACTOR, A4_OFFSET_LEFT_MICROMETER - A4_OFFSET_LEFT_PIXEL * PIXEL_TO_MICROMETER_FACTOR, A4_OFFSET_TOP_MICROMETER - A4_OFFSET_TOP_PIXEL * PIXEL_TO_MICROMETER_FACTOR)

		frame = box(A4_OFFSET_LEFT_MICROMETER, A4_OFFSET_TOP_MICROMETER, A4_OFFSET_LEFT_MICROMETER + A4_WIDTH_MICROMETER, A4_OFFSET_TOP_MICROMETER + A4_HEIGHT_MICROMETER)
		plot.add_polygon(frame)

		# plot A5 frame
		frame = box(A5_OFFSET_LEFT_MICROMETER, A5_OFFSET_TOP_MICROMETER, A5_OFFSET_LEFT_MICROMETER + A5_WIDTH_MICROMETER, A5_OFFSET_TOP_MICROMETER + A5_HEIGHT_MICROMETER)
		plot.add_polygon(frame, color=solved_color)

		for piece in pieces:
			plot.add_polygon(piece.polygon)
			plot.add_point(piece.polygon.centroid)

			for edge in piece.edges:
				if not edge.is_frame_edge:
					continue

				plot.add_line(edge.line)

			if piece.placed_piece is not None:
				plot.add_polygon(piece.placed_piece.polygon, color=solved_color)
				plot.add_point(piece.placed_piece.polygon.centroid)

		plot.show()
