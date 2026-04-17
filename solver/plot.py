import cv2
import numpy as np
from shapely import LineString, Point
from shapely.geometry import Polygon

class Plot:
	def __init__(self, window_name="Plot"):
		self.window_name = window_name
		self.items = []

	def addImage(self, image):
		if image is None:
			raise ValueError("Image cannot be None")

		self.items.append({
			"image": self.__ensure_bgr(image),
			"polygons": [],
			"points": [],
			"lines": []
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

	def addPoint(self, point: Point, color=(0, 0, 255), radius=5, image_index=-1):
		if not self.items:
			raise RuntimeError("Add an image before adding points.")

		target = self.items[image_index]
		target["points"].append({
			"point": point,
			"color": color,
			"radius": radius
		})

	def addLine(self, line: LineString, color=(255, 0, 0), thickness=2, arrow=True, image_index=-1):
		if not self.items:
			raise RuntimeError("Add an image before adding lines.")

		if not isinstance(line, LineString):
			raise TypeError("line must be a shapely.geometry.LineString")

		target = self.items[image_index]
		target.setdefault("lines", []).append({
			"line": line,
			"color": color,
			"thickness": thickness,
			"arrow": arrow
		})

	def __ensure_bgr(self, img):
		if len(img.shape) == 2:
			return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
		if img.shape[2] == 1:
			return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
		return img

	def __draw_polygon(self, img, polygon, color, thickness):
		# exterior coords
		coords = np.array(list(polygon.exterior.coords), dtype=np.int32)
		cv2.polylines(img, [coords], isClosed=True, color=color, thickness=thickness)

		# holes (if any)
		for interior in polygon.interiors:
			hole = np.array(list(interior.coords), dtype=np.int32)
			cv2.polylines(img, [hole], isClosed=True, color=(0, 0, 255), thickness=thickness)

	def __draw_point(self, img, point, color, radius):
		x, y = int(point.x), int(point.y)
		cv2.circle(img, (x, y), radius, color, -1)

	def __draw_line(self, img, line, color, thickness, arrow):
		coords = list(line.coords)

		if len(coords) < 2:
			return

		pts = np.array(coords, dtype=np.int32)

		# Draw polyline
		cv2.polylines(img, [pts], isClosed=False, color=color, thickness=thickness)

		# Draw arrow on last segment
		if arrow:
			p1 = pts[-2]
			p2 = pts[-1]

			cv2.arrowedLine(
				img,
				tuple(p1),
				tuple(p2),
				color,
				thickness,
				tipLength=0.1  # adjust arrow size
			)

	def show(self, wait=True, resize=None):
		for i, item in enumerate(self.items):
			img = item["image"].copy()

			for polygon in item["polygons"]:
				self.__draw_polygon(img, polygon["polygon"], polygon["color"], polygon["thickness"])

			for point in item["points"]:
				self.__draw_point(img, point["point"], point["color"], point["radius"])

			for line in item["lines"]:
				self.__draw_line(
					img,
					line["line"],
					line["color"],
					line["thickness"],
					line["arrow"]
				)

			if resize is not None:
				img = cv2.resize(img, resize)

			window = f"{self.window_name}_{i}" if len(self.items) > 1 else self.window_name
			cv2.imshow(window, img)

		if wait:
			cv2.waitKey(0)
			cv2.destroyAllWindows()
