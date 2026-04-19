from typing import List

import cv2
import numpy as np
from shapely import LineString, Point, Polygon
from shapely.affinity import scale, translate

IMAGE_SCALE = 0.003
PICKER_ORIGIN_OFFSET_MM = (int(80000 * IMAGE_SCALE), int(80000 * IMAGE_SCALE))
PICKER_PLANE_MM = (int(350000 * IMAGE_SCALE), int(350000 * IMAGE_SCALE))

class Plot:
	def __init__(self, window_name="Plot"):
		self.window_name = window_name
		self.canvas = np.ones((PICKER_PLANE_MM[0] + PICKER_ORIGIN_OFFSET_MM[0], PICKER_PLANE_MM[1] + PICKER_ORIGIN_OFFSET_MM[1], 3), dtype=np.uint8) * 255  # white background

	def add_image(self, image, scale: float, offsetX: int, offsetY: int):
		scale *= IMAGE_SCALE
		image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)

		offsetX = int(offsetX * IMAGE_SCALE) + PICKER_ORIGIN_OFFSET_MM[0]
		offsetY = int(offsetY * IMAGE_SCALE) + PICKER_ORIGIN_OFFSET_MM[1]

		canvas_h, canvas_w = self.canvas.shape[:2]
		img_h, img_w = image.shape[:2]

		# Source and destination start positions
		src_x0 = max(0, -offsetX)
		src_y0 = max(0, -offsetY)

		dst_x0 = max(0, offsetX)
		dst_y0 = max(0, offsetY)

		# Remaining space in canvas from destination point
		dst_w = canvas_w - dst_x0
		dst_h = canvas_h - dst_y0

		# Corresponding remaining image size from source point
		src_w = img_w - src_x0
		src_h = img_h - src_y0

		# Final overlap size
		w = min(dst_w, src_w)
		h = min(dst_h, src_h)

		if w <= 0 or h <= 0:
			return  # nothing visible on canvas

		cropped = image[src_y0:src_y0 + h, src_x0:src_x0 + w]

		self.canvas[dst_y0:dst_y0 + h, dst_x0:dst_x0 + w] = cropped

	def add_point(self, point: Point, radius=3, color=(0, 0, 255)):
		point = translate(scale(point, IMAGE_SCALE, IMAGE_SCALE, 1, (0, 0)),  PICKER_ORIGIN_OFFSET_MM[0], PICKER_ORIGIN_OFFSET_MM[1])
		x, y = int(point.x), int(point.y)

		cv2.circle(self.canvas, (x, y), radius, color, -1)

	def add_line(self, line: LineString, color=(255, 0, 0), thickness=2):
		line = translate(scale(line, IMAGE_SCALE, IMAGE_SCALE, 1, (0, 0)),  PICKER_ORIGIN_OFFSET_MM[0], PICKER_ORIGIN_OFFSET_MM[1])
		coords = list(line.coords)

		if len(coords) < 2:
			return

		points = np.array(coords, dtype=np.int32)

		cv2.polylines(self.canvas, [points], isClosed=False, color=color, thickness=thickness)

		point1 = points[-2]
		point2 = points[-1]

		cv2.arrowedLine(self.canvas, tuple(point1), tuple(point2), color, thickness, tipLength=0.1)

	def add_polygon(self, polygon: Polygon, color=(0, 255, 0), thickness=2):
		polygon = translate(scale(polygon, IMAGE_SCALE, IMAGE_SCALE, 1, (0, 0)),  PICKER_ORIGIN_OFFSET_MM[0], PICKER_ORIGIN_OFFSET_MM[1])
		coords = np.array(list(polygon.exterior.coords), dtype=np.int32)

		cv2.polylines(self.canvas, [coords], isClosed=True, color=color, thickness=thickness)

	def show(self):
		# draw offset lines
		x0, y0 = PICKER_ORIGIN_OFFSET_MM
		w, h = PICKER_PLANE_MM
		cv2.rectangle(self.canvas, (x0, y0), (x0 + w, y0 + h), (0, 0, 255), thickness=1)

		cv2.imshow(self.window_name, self.canvas)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
