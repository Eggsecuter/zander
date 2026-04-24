from typing import List, Optional
from shapely import Polygon
from shapely.geometry.point import Point
from shapely.affinity import rotate, translate

from solver.models.edge import Edge
from solver.models.placed_piece import PlacedPiece


class Piece:
	def __init__(self, polygon: Polygon, edges: List[Edge]):
		self.polygon = polygon
		self.edges = edges
		self.placed_piece: Optional[PlacedPiece] = None

	def place(self, edge_index: int, cursor: Point, angle_degrees: float):
		edge = self.edges[edge_index]

		# rotation needed to match desired direction
		rotation_degrees = angle_degrees - edge.angle_degrees

		rotated_polygon = rotate(self.polygon, rotation_degrees, origin=(edge.startX, edge.startY), use_radians=False)
		placed_polygon = translate(rotated_polygon, cursor.x - edge.startX, cursor.y - edge.startY)

		self.placed_piece = PlacedPiece(placed_polygon, rotation_degrees)

	def reset(self):
		self.placed_piece = None
