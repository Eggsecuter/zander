import copy
import math
from typing import List

from solver.models.edge import Edge
from solver.models.frame_side import FrameSide
from solver.models.piece import Piece
from solver.models.place_transform import PlaceTransform
from solver.models.puzzle_frame import PuzzleFrame
from solver.models.vector2 import Vector2

# TODO define real world margin
PUZZLE_PIECE_MARGIN = 0.5

class Matcher2:
	def __init__(self, frame: PuzzleFrame, pieces: List[Piece]):
		self.frame = frame
		self.pieces = pieces

		# used for orientation during solving
		self.cursor: Vector2 = Vector2(0, 0) # current position for edge matching
		self.current_direction: float = 0 # radiant
		self.last_turn: Vector2 = None
		self.last_completed_side: FrameSide = None
