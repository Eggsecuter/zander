import cv2
import numpy as np

class ImageLoader:
	@staticmethod
	def from_path(path):
		image = cv2.imread(path)

		if image is None:
			raise FileNotFoundError(f"Image not found: {path}")

		return ImageLoader.__clean(image)

	@staticmethod
	def from_buffer(buffer: bytearray):
		array = np.frombuffer(buffer, np.uint8)
		image = cv2.imdecode(array, cv2.IMREAD_COLOR)

		if image is None:
			raise ValueError("Invalid image bytes")

		return ImageLoader.__clean(image)

	@staticmethod
	def __clean(image):
		grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		blurred = cv2.GaussianBlur(grayscale, (5, 5), 0)

		_, threshold = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

		return threshold
