from typing import List
from shapely import Polygon

from solver.models.edge import Edge


class PlacedPiece:
	def __init__(self, polygon: Polygon, edges: List[Edge], rotation_degrees: float):
		self.polygon = polygon
		self.edges = edges
		self.rotation_degrees = rotation_degrees
