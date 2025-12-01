
import math
from dataclasses import dataclass
from typing import List

from solver.models.vector2 import Vector2


@dataclass
class Edge:
	'''
	Edges can have 2-5 points. This allows combined edges where we can automatically slide the cursor along all corners.
	Combined edges also prevent trying to place edges where the left "connecting" edge also is a frame edge (which is not allowed).

	The shape points of the "parent" also must be passed in and updated when translated or rotated that the edge can access point data and calculate various useful data.
	'''
	shape_points: List[Vector2]
	point_indices: List[int]

	@property
	def start(self):
		return self.shape_points[self.point_indices[0]]

	@property
	def end(self):
		return self.shape_points[self.point_indices[-1]]

	@property
	def corner_count(self):
		return len(self.points) - 2

	def get_length(self):
		length: float = 0

		for index in range(len(self.point_indices) - 1):
			line_start = self.shape_points[self.point_indices[index]]
			line_end = self.shape_points[self.point_indices[index + 1]]

			length += math.hypot(line_end.x - line_start.x, line_end.y - line_start.y)

		return length

	def get_start_angle(self):
		'''
		Get angle of first line (first two points) in edge
		'''
		return self.start.angle_to(self.shape_points[self.point_indices[1]])

	def get_end_angle(self):
		'''
		Get angle of last line (last two points) in edge
		'''
		return self.shape_points[self.point_indices[-2]].angle_to(self.end)
