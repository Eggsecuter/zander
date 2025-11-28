import cv2
import numpy as np

from typing import Tuple

class ShapeDetector:
	@staticmethod
	def detect(image):
		gradient_x = cv2.Sobel(image, cv2.CV_16S, 1, 0)
		gradient_y = cv2.Sobel(image, cv2.CV_16S, 0, 1)

		gradient_x_abs = np.abs(gradient_x)
		gradient_y_abs = np.abs(gradient_y)

		# TODO normalize values (absolute pixel coordinates -> percentage coordinates -> absolute robot coordinates)

		return np.minimum(gradient_x_abs + gradient_y_abs, 255).astype(np.uint8)
