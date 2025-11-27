import cv2
import numpy as np
import os

class ImageLoader:
	@staticmethod
	def from_path(path):
		image = cv2.imread(path)

		if image is None:
			raise FileNotFoundError(f"Image not found: {path}")

		return image

	@staticmethod
	def from_buffer(buffer: bytearray):
		array = np.frombuffer(buffer, np.uint8)
		image = cv2.imdecode(array, cv2.IMREAD_COLOR)

		if image is None:
			raise ValueError("Invalid image bytes")

		return image
