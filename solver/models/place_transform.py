from dataclasses import dataclass

from solver.models.vector_2 import Vector2


@dataclass
class PlaceTransform:
	transposition: Vector2
	rotation_degrees: float
