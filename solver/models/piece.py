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

	def get_placed_piece(self) -> Piece:
		piece = copy.deepcopy(self)

		#
		# transposition (absolute)
		#
		old_center = piece.center_of_mass  # original center
		new_center = piece.place_transform.position
		dx = new_center.x - old_center.x
		dy = new_center.y - old_center.y

		# translate points
		piece.points = [Vector2(p.x + dx, p.y + dy) for p in piece.points]

		# translate edges
		piece.edges = [Edge(Vector2(e.start.x + dx, e.start.y + dy),
							Vector2(e.end.x + dx, e.end.y + dy))
					for e in piece.edges]

		# update center_of_mass
		piece.center_of_mass = Vector2(new_center.x, new_center.y)

		#
		# rotation (relative)
		#
		cos_rotation = math.cos(piece.place_transform.rotation_radiant)
		sin_rotation = math.sin(piece.place_transform.rotation_radiant)

		# rotate all points around center of mass
		rotated_points = []

		for point in piece.points:
			tx = point.x - piece.center_of_mass.x
			ty = point.y - piece.center_of_mass.y

			rx = tx * cos_rotation - ty * sin_rotation
			ry = tx * sin_rotation + ty * cos_rotation

			rotated_points.append(Vector2(piece.center_of_mass.x + rx, piece.center_of_mass.y + ry))

		piece.points = rotated_points

		# rotate edges too
		rotated_edges = []

		for edge in piece.edges:
			def rotate(vector):
				tx = vector.x - piece.center_of_mass.x
				ty = vector.y - piece.center_of_mass.y
				rx = tx * cos_rotation - ty * sin_rotation
				ry = tx * sin_rotation + ty * cos_rotation
				return Vector2(piece.center_of_mass.x + rx, piece.center_of_mass.y + ry)

			rotated_edges.append(Edge(rotate(edge.start), rotate(edge.end)))

		piece.edges = rotated_edges

		return piece
