from dataclasses import dataclass, field
from typing import List

from solver.models.edge import Edge
from solver.models.vector_2 import Vector2
from solver.utility.polygon import Polygon

@dataclass
class Piece:
	points: List[Vector2]

	# grip point
	center_of_mass: Vector2 = field(init=False)
	edges: List[Edge] = field(init=False)

	def __post_init__(self):
		self.center_of_mass = Polygon.calculate_center_of_mass(self.points)
		self.edges = Polygon.calculate_edges(self.points)
