from typing import List
import numpy as np
from shapely import LineString, Polygon

from solver.models.placed_piece import PlacedPiece


class Piece:
	@property
	def is_placed(self) -> bool:
		return self.placed_piece is not None

	def __init__(self, polygon: Polygon, edges: List[LineString]):
		self.polygon = polygon
		self.edges = edges

	def place(self, polygon: Polygon, rotation: float):
		self.placed_piece = PlacedPiece(polygon, rotation)
