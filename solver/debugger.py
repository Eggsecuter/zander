from typing import List
from solver.plot import Plot


class Debugger:
	__enabled: bool = False

	@staticmethod
	def enable():
		Debugger.__enabled = True

	@staticmethod
	def log(message: str):
		if Debugger.__enabled:
			print(message)

	@staticmethod
	def plot(image, pieces):
		plot = Plot()
		plot.addImage(image)

		for piece in pieces:
			plot.addPolygon(piece.original, thickness=5)
			plot.addPoint(piece.original.centroid)

			for edge in piece.edges:
				plot.addLine(edge, color=(255, 0, 0), thickness=3)

		plot.show()
