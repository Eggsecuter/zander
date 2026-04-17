from typing import List
import numpy as np
from shapely import LineString, Polygon

from solver.models.placed_piece import PlacedPiece


class Piece:
	def __init__(self, polygon: Polygon, edges: List[LineString]):
		self.polygon = polygon
		self.edges = edges

	def place(self, polygon: Polygon, rotation: float):
		self.placedPiece = PlacedPiece(polygon, rotation)
