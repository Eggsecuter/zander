from typing import List

import numpy as np
from shapely import LineString, Polygon


class Piece:
	def __init__(self, original: Polygon, edges: List[LineString]):
		self.original = original
		self.edges = edges

	def place(self, placed: Polygon):
		self.placed = placed
