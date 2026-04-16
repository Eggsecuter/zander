import cv2
import numpy as np
from shapely.geometry import Polygon

class Plot:
	def __init__(self, window_name="Plot"):
		self.window_name = window_name
		self.items = []

	def addImage(self, image):
		if image is None:
			raise ValueError("Image cannot be None")

		image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

		self.items.append({
			"image": self._ensure_bgr(image),
			"polygons": []
		})

	def addPolygon(self, polygon: Polygon, color=(0, 255, 0), thickness=2 , image_index=-1):
		if not self.items:
			raise RuntimeError("Add an image before adding polygons.")

		if not isinstance(polygon, Polygon):
			raise TypeError("polygon must be a shapely.geometry.Polygon")

		# store on selected image (default last)
		target = self.items[image_index]
		target["polygons"].append({
			"polygon": polygon,
			"color": color,
			"thickness": thickness
		})

	def _ensure_bgr(self, img):
		if len(img.shape) == 2:
			return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
		if img.shape[2] == 1:
			return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
		return img

	def _draw_polygon(self, img, polygon, color, thickness):
		# exterior coords
		coords = np.array(list(polygon.exterior.coords), dtype=np.int32)
		cv2.polylines(img, [coords], isClosed=True, color=color, thickness=thickness)

		# holes (if any)
		for interior in polygon.interiors:
			hole = np.array(list(interior.coords), dtype=np.int32)
			cv2.polylines(img, [hole], isClosed=True, color=(0, 0, 255), thickness=thickness)

	def show(self, wait=True, resize=None):
		for i, item in enumerate(self.items):
			img = item["image"].copy()

			for p in item["polygons"]:
				self._draw_polygon(img, p["polygon"], p["color"], p["thickness"])

			if resize is not None:
				img = cv2.resize(img, resize)

			window = f"{self.window_name}_{i}" if len(self.items) > 1 else self.window_name
			cv2.imshow(window, img)

		if wait:
			cv2.waitKey(0)
			cv2.destroyAllWindows()
