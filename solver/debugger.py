import os
from typing import List

from shapely import Point
from solver.plot import Plot
from solver.constants import *


class Debugger:
	__enabled: bool = False

	@staticmethod
	def enable():
		Debugger.__enabled = True

	@staticmethod
	def log(message: str):
		if not Debugger.__enabled:
			return

		print(message)

	@staticmethod
	def plot(image, pieces):
		if not Debugger.__enabled:
			return

		if os.name != "nt":
			if "DISPLAY" not in os.environ:
				return

		try:
			plot = Plot()
			plot.addImage(image)

			plot.addPoint(Point((A4_OFFSET_LEFT_PIXEL, A4_OFFSET_TOP_PIXEL)))
			plot.addPoint(Point((A4_OFFSET_LEFT_PIXEL + A4_WIDTH_MICROMETER / PIXEL_TO_MICROMETER_FACTOR, A4_OFFSET_TOP_PIXEL + A4_HEIGHT_MICROMETER / PIXEL_TO_MICROMETER_FACTOR)))

			for piece in pieces:
				plot.addPolygon(piece.polygon, thickness=5)
				plot.addPoint(piece.polygon.centroid)

				for edge in piece.edges:
					plot.addLine(edge, color=(255, 0, 0), thickness=3)

			plot.show()
		except:
			return
