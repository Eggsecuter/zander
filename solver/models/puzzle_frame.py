from dataclasses import dataclass

from solver.models.vector_2 import Vector2


@dataclass
class PuzzleFrame:
	topLeft: Vector2
	topRight: Vector2
	bottomLeft: Vector2
	bottomRight: Vector2
