from typing import List, Optional
from shapely import Polygon
from shapely.geometry.point import Point
from shapely.affinity import rotate, translate

from solver.models.cursor import Cursor
from solver.models.edge import Edge
from solver.models.placed_piece import PlacedPiece


class Piece:
	def __init__(self, polygon: Polygon, edges: List[Edge]):
		self.polygon = polygon
		self.edges = edges
		self.placed_piece: Optional[PlacedPiece] = None

	def place(self, edge_index: int, cursor: Cursor):
		current_edge = self.edges[edge_index]
		x_offset = cursor.point.x - current_edge.startX
		y_offset = cursor.point.y - current_edge.startY

		# rotation needed to match desired direction
		rotation_degrees = cursor.angle_degrees - current_edge.angle_degrees

		rotated_polygon = rotate(self.polygon, rotation_degrees, origin=(current_edge.startX, current_edge.startY), use_radians=False)
		placed_polygon = translate(rotated_polygon, x_offset, y_offset)

		placed_edges: List[Edge] = []

		for edge in self.edges:
			rotated_line = rotate(edge.line, rotation_degrees, origin=(current_edge.startX, current_edge.startY), use_radians=False)
			placed_line = translate(rotated_line, x_offset, y_offset)

			placed_edges.append(Edge(placed_line, edge.is_frame_edge))

		self.placed_piece = PlacedPiece(placed_polygon, placed_edges, rotation_degrees)

	def reset(self):
		self.placed_piece = None
