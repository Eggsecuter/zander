import cv2
import numpy as np

from typing import List, Tuple
from solver.models.piece import Piece
from solver.models.puzzle_frame import PuzzleFrame
from solver.models.vector_2 import Vector2
from solver.utility.polygon import PolygonUtility

FRAME_WIDTH_PERCENTAGE = 30

class PieceDetector:
	@staticmethod
	def detect(image) -> Tuple[PuzzleFrame, List[Piece]]:
		contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

		# define boundary for frame
		left_boundary = int(image.shape[1] * FRAME_WIDTH_PERCENTAGE / 100)

		frame: PuzzleFrame = None
		pieces: List[Piece] = []

		for contour in contours:
			# convert contour to Nx2 array
			coordinates = contour.reshape(-1, 2)

			# skip frame
			if np.any(coordinates[:, 0] < left_boundary): # frame
				frame = PolygonUtility.get_frame(coordinates)
			else: # piece
				vectors = [Vector2(x=int(pt[0]), y=int(pt[1])) for pt in coordinates]
				piece = Piece(vectors)
				pieces.append(piece)

		return frame, pieces
