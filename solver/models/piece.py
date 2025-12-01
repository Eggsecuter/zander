from dataclasses import dataclass, field
from typing import List
import copy

from solver.models.edge import Edge
from solver.models.place_transform import PlaceTransform
from solver.models.vector2 import Vector2

@dataclass
class Piece:
	points: List[Vector2]
	center_of_mass: Vector2 # robot grip point
	edges: List[Edge]
	place_transform: PlaceTransform = field(init=False)

	def __post_init__(self):
		# gets calculated during matching
		self.place_transform = PlaceTransform(copy.deepcopy(self.center_of_mass), 0)
