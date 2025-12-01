import cv2
import numpy as np

from typing import Tuple

class ShapeDetector:
	@staticmethod
	def detect(image):
		gradient_x = cv2.Sobel(image, cv2.CV_16S, 1, 0)
		gradient_y = cv2.Sobel(image, cv2.CV_16S, 0, 1)

		abs
		gradient_x_absolute = abs(gradient_x)
		gradient_y_absolute = abs(gradient_y)

		return np.minimum(gradient_x_absolute + gradient_y_absolute, 255).astype(np.uint8)
