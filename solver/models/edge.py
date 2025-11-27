
from dataclasses import dataclass
from typing import List

from solver.models.vector_2 import Vector2


@dataclass
class Edge:
	points: List[Vector2]
