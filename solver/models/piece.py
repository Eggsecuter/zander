from dataclasses import dataclass, field
from typing import List
import copy
import math

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
		self.place_transform = PlaceTransform(copy.deepcopy(self.center_of_mass), 0)

	def get_placed_piece(self):
		piece = copy.deepcopy(self)
		piece.center_of_mass = Vector2(self.place_transform.position.x, self.place_transform.position.y)

		translation = piece.center_of_mass - self.center_of_mass

		for index in range(len(piece.points)):
			piece.points[index] = piece.points[index].rotate_around(self.center_of_mass, self.place_transform.rotation_radiant) + translation

		for index in range(len(piece.edges)):
			piece.edges[index].start = piece.edges[index].start.rotate_around(self.center_of_mass, self.place_transform.rotation_radiant) + translation
			piece.edges[index].end = piece.edges[index].end.rotate_around(self.center_of_mass, self.place_transform.rotation_radiant) + translation

		return piece
