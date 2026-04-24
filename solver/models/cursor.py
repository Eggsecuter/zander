from shapely import Point


class Cursor:
	def __init__(self, point: Point, angle_degrees: float):
		self.point = point
		self.angle_degrees = angle_degrees
