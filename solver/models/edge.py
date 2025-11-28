
import math
import numpy as np
from dataclasses import dataclass
from typing import List

from solver.models.vector_2 import Vector2


@dataclass
class Edge:
	start: Vector2
	end: Vector2

	def get_angle(self):
		dx = self.end.x - self.start.x
		dy = self.end.y - self.start.y

		return math.atan2(dy, dx)

	def get_length(self):
		return np.hypot(self.end.x - self.start.x, self.end.y - self.start.y)
