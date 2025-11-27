from typing import List
from solver.models.edge import Edge
from solver.models.vector_2 import Vector2


class Polygon:
	@staticmethod
	def calculate_center_of_mass(points: List[Vector2]) -> Vector2:
		area = 0.0
		cx = 0.0
		cy = 0.0
		n = len(points)

		for i in range(n):
			current = points[i]
			next_point = points[(i + 1) % n]  # wrap around
			cross = current.x * next_point.y - next_point.x * current.y
			area += cross
			cx += (current.x + next_point.x) * cross
			cy += (current.y + next_point.y) * cross

		area *= 0.5
		cx /= (6 * area)
		cy /= (6 * area)

		return Vector2(cx, cy)

	@staticmethod
	def calculate_edges(points: List[Vector2], margin=1.0) -> List[Edge]:
		return []
