import math
from typing import List
from shapely import LineString, Polygon
from shapely.geometry.point import Point
from shapely.affinity import rotate, translate

from solver.models.placed_piece import PlacedPiece


class Piece:
	@property
	def is_placed(self) -> bool:
		return self.placed_piece is not None

	def __init__(self, polygon: Polygon, edges: List[LineString]):
		self.polygon = polygon
		self.edges = edges

	def place(self, edgeIndex: int, cursor: Point, angle_degrees: float):
		edge = self.edges[edgeIndex]

		# extract start and end of edge
		startX, startY = edge.coords[0]
		endX, endY = edge.coords[-1]

		# current angle of the edge (degrees)
		current_angle_degrees = math.degrees(math.atan2(endY - startY, endX - startX))

		# rotation needed to match desired direction
		rotation_degrees = angle_degrees - current_angle_degrees

		rotated_polygon = rotate(self.polygon, rotation_degrees, origin=(startX, startY), use_radians=False)
		placed_polygon = translate(rotated_polygon, cursor.x - startX, cursor.y - startY)

		self.placed_piece = PlacedPiece(placed_polygon, rotation_degrees)

	def reset(self):
		self.placed_piece = None
