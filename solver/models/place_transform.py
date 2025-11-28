from dataclasses import dataclass

from solver.models.vector_2 import Vector2


@dataclass
class PlaceTransform:
	position: Vector2 # absolute
	rotation_radiant: float # relative
