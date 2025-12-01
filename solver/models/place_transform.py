from dataclasses import dataclass

from solver.models.vector2 import Vector2


@dataclass
class PlaceTransform:
	'''
	Translation and rotation needed for target transform in puzzle frame.

	This data is used for the robot. Thus the position is absolute and the rotation relative.
	'''
	position: Vector2 # absolute
	rotation_radiant: float # relative
