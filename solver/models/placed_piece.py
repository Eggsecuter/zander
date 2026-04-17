from typing import List
from shapely import Polygon


class PlacedPiece:
	def __init__(self, polygon: Polygon, rotation: float):
		self.polygon = polygon
		self.rotation = rotation
