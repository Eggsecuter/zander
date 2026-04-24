from typing import List
from solver.models.piece import Piece


class Solution:
	def __init__(self, pieces: List[Piece], score: float):
		self.pieces = pieces
		self.score = score
