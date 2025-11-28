from dataclasses import dataclass, field
from typing import List

from solver.models.edge import Edge
from solver.models.place_transform import PlaceTransform
from solver.models.vector_2 import Vector2
from solver.utility.polygon import PolygonUtility

@dataclass
class Piece:
	points: List[Vector2]

	# grip point
	center_of_mass: Vector2 = field(init=False)
	edges: List[Edge] = field(init=False)
	place_transform: PlaceTransform = field(init=False)

	def __post_init__(self):
		self.points = PolygonUtility.roughen(self.points)

		self.center_of_mass = PolygonUtility.calculate_center_of_mass(self.points)
		self.edges = PolygonUtility.calculate_edges(self.points)

		# gets calculated while matching
		self.place_transform = None
