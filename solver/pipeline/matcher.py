from typing import List

from solver.models.piece import Piece
from solver.models.place_transform import PlaceTransform
from solver.models.puzzle_frame import PuzzleFrame
from solver.models.vector_2 import Vector2


class Matcher:
	@staticmethod
	def solve(frame: PuzzleFrame, pieces: List[Piece]):
		# For each corner combination (4 pieces -> 6 * 4 = 24 possibilities):
			# Place every corner piece
			# Calculate the needed transformation and rotation that the piece sits tightly in the frame, relative to the grip point

			# For each side combination (0 or 2 pieces -> 2 possibilities):
				# Place every side piece
				# Calculate the needed transformation and rotation that the piece sits tightly in the frame, relative to the grip point

				# Measure the overlap % inside the frame
				# Save the accuracy and the instructions for each piece to the result list

		# Return the result with the best accuracy (least overlap %)

		for piece in pieces:
			piece.place_transform = PlaceTransform(Vector2(0, 0), 0)
