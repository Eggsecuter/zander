from shapely import Polygon


class PlacedPiece:
	def __init__(self, polygon: Polygon, rotation_degrees: float):
		self.polygon = polygon
		self.rotation_degrees = rotation_degrees
