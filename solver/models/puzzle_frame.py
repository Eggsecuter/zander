from enum import Enum
from dataclasses import dataclass

from solver.models.vector_2 import Vector2

class FrameSide(Enum):
	LONG = 'long'
	SHORT = 'short'

@dataclass
class PuzzleFrame:
	topLeft: Vector2
	topRight: Vector2
	bottomLeft: Vector2
	bottomRight: Vector2

	def get_width(self):
		top_width = abs(self.topRight.x - self.topLeft.x)
		bottom_width = abs(self.bottomRight.x - self.bottomLeft.x)
		return (top_width + bottom_width) / 2

	def get_height(self):
		left_height = abs(self.bottomLeft.y - self.topLeft.y)
		right_height = abs(self.bottomRight.y - self.topRight.y)
		return (left_height + right_height) / 2
