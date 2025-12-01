from dataclasses import dataclass, field
from typing import List

from solver.models.edge import Edge
from solver.models.piece import Piece
from solver.models.place_transform import PlaceTransform
from solver.models.vector2 import Vector2


@dataclass
class PlacedPiece:
	'''
	How the piece would look like when the place transform is done. Used during matching and for plotter (visualization during development)
	'''
	center_of_mass: Vector2
	points: List[Vector2] = field(init=False)
	edges: List[Edge] = field(init=False)

	def __post_init__(self):
		self.points = []
		self.edges = []

	@staticmethod
	def get_from(original: Piece):
		placed_piece = PlacedPiece(
			original.place_transform.position.copy()
		)

		translation = placed_piece.center_of_mass - original.center_of_mass

		for original_point in original.points:
			placed_point = original_point.rotate_around(original.center_of_mass, original.place_transform.rotation_radiant) + translation
			placed_piece.points.append(placed_point)

		for original_edge in original.edges:
			placed_edge = Edge(placed_piece.points, list(original_edge.point_indices))
			placed_piece.edges.append(placed_edge)

		return placed_piece
