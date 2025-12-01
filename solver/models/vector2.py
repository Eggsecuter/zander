import math
from dataclasses import dataclass

@dataclass
class Vector2:
	x: float
	y: float

	def copy(self) -> Vector2:
		return Vector2(self.x, self.y)

	def angle_to(self, other: Vector2) -> float:
		distance_x = other.x - self.x
		distance_y = other.y - self.y

		return math.atan2(distance_y, distance_x)

	def distance_to(self, other: Vector2) -> float:
		return math.hypot(self.x - other.x, self.y - other.y)

	def rotate_around(self, center: Vector2, angle: float) -> Vector2:
		# translate point to origin
		origin = self - center

		# rotate
		x_new = origin.x * math.cos(angle) - origin.y * math.sin(angle)
		y_new = origin.x * math.sin(angle) + origin.y * math.cos(angle)

		# translate back
		return Vector2(x_new + center.x, y_new + center.y)

	def __add__(self, other: Vector2) -> Vector2:
		return Vector2(self.x + other.x, self.y + other.y)

	def __sub__(self, other: Vector2) -> Vector2:
		return Vector2(self.x - other.x, self.y - other.y)
