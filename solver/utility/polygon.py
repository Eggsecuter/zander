import cv2
import numpy as np
import math

from shapely.geometry import LineString, Polygon
from typing import List
from solver.models.edge import Edge
from solver.models.puzzle_frame import PuzzleFrame
from solver.models.vector_2 import Vector2

ROUGHENING_EPSILON: float = 0.5
EDGE_LINE_MARGIN: float = 0.1
EDGE_CONNECTION_MARGIN: float = 1.0
EDGE_CONNECTION_ANGLE_MARGIN_DEGREES: float = 10.0

class PolygonUtility:
	@staticmethod
	def roughen(points: List[Vector2], epsilon=ROUGHENING_EPSILON) -> List[Vector2]:
		if len(points) < 3:
			return points

		# find point with max distance from line (points[0] -> points[-1])
		max_dist = 0
		index = 0

		for i in range(1, len(points) - 1):
			dist = PolygonUtility.perpendicular_distance(points[i], points[0], points[-1])
			if dist > max_dist:
				index = i
				max_dist = dist

		# if max distance > epsilon: recurse
		if max_dist > epsilon:
			left = PolygonUtility.roughen(points[:index+1], epsilon)
			right = PolygonUtility.roughen(points[index:], epsilon)

			return  left[:-1] + right
		else:
			# all points lie close to a line → keep only endpoints
			return [points[0], points[-1]]

	@staticmethod
	def calculate_center_of_mass(points: List[Vector2]) -> Vector2:
		if len(points) == 0:
			return Vector2(0, 0)

		area = 0.0
		cx = 0.0
		cy = 0.0
		n = len(points)

		for i in range(n):
			current = points[i]
			next_point = points[(i + 1) % n]  # wrap around
			cross = current.x * next_point.y - next_point.x * current.y
			area += cross
			cx += (current.x + next_point.x) * cross
			cy += (current.y + next_point.y) * cross

		area *= 0.5

		cx /= (6 * area)
		cy /= (6 * area)

		return Vector2(cx, cy)

	@staticmethod
	def calculate_edges(points: List[Vector2], line_margin=EDGE_LINE_MARGIN, connection_margin=EDGE_CONNECTION_MARGIN, angle_margin_deg=EDGE_CONNECTION_ANGLE_MARGIN_DEGREES) -> List[Edge]:
		edges: List[Edge] = []
		n = len(points)
		start = 0

		while start < n:
			end = start + 1

			while end < n:
				segment = points[start:end+1]
				a = segment[0]
				b = segment[-1]

				# 1) collinearity check
				if not all(PolygonUtility.distance_point_to_line(p, a, b) <= line_margin
							for p in segment):
					break

				# 2) infinite-line must NOT intersect polygon
				if PolygonUtility.line_intersects_polygon(a, b, points, start, end):
					break

				# 3) polygon must lie entirely on ONE SIDE of infinite line AB
				if not PolygonUtility.is_polygon_one_side(a, b, points, start, end):
					break

				end += 1

			# Edge must have at least two points
			if end - start >= 2:
				edges.append(Edge(points[start], points[end - 1]))

			start = end

		# TODO assumption for classic jigsaw puzzle pieces -> take all edges into account for better algorithm
		edges.sort(key=lambda e: e.get_length(), reverse=True)

		if len(edges) < 2:
			return edges  # only one edge available

		e1, e2 = edges[0], edges[1]

		# --- Check if edges are connected ---
		def connected(e1, e2, margin):
			points1 = [e1.start, e1.end]
			points2 = [e2.start, e2.end]
			for p1 in points1:
				for p2 in points2:
					if math.hypot(p1.x - p2.x, p1.y - p2.y) <= margin:
						return True
			return False

		if not connected(e1, e2, connection_margin):
			return [e1]  # not connected

		# --- Check if angle between edges is ~90 degrees ---
		def edge_vector(e):
			return e.end.x - e.start.x, e.end.y - e.start.y

		v1x, v1y = edge_vector(e1)
		v2x, v2y = edge_vector(e2)

		# Cosine of angle
		dot = v1x*v2x + v1y*v2y
		len1 = math.hypot(v1x, v1y)
		len2 = math.hypot(v2x, v2y)

		if len1 == 0 or len2 == 0:
			return [e1]  # avoid division by zero

		cos_angle = dot / (len1 * len2)
		angle_deg = math.degrees(math.acos(max(min(cos_angle, 1), -1)))  # clamp due to fp errors

		if abs(angle_deg - 90) <= angle_margin_deg:
			return [e1, e2]  # connected and ~90°
		else:
			return [e1]

	# -------------------------------------------------------------------------
	# Point–line distance
	# -------------------------------------------------------------------------
	@staticmethod
	def distance_point_to_line(p, a, b):
		px, py = p.x, p.y
		ax, ay = a.x, a.y
		bx, by = b.x, b.y

		if ax == bx and ay == by:
			return np.hypot(px - ax, py - ay)

		return abs((by - ay) * px - (bx - ax) * py + bx * ay - by * ax) / np.hypot(by - ay, bx - ax)

	# -------------------------------------------------------------------------
	# Check if infinite line AB intersects the polygon (except the segment itself)
	# -------------------------------------------------------------------------
	@staticmethod
	def line_intersects_polygon(a, b, points, start_idx, end_idx):
		n = len(points)

		for i in range(n):
			j = (i + 1) % n

			# skip edges of the current segment
			if start_idx - 1 <= i <= end_idx:
				continue

			p1 = points[i]
			p2 = points[j]

			if PolygonUtility.segments_intersect(a, b, p1, p2):
				return True

		return False

	# -------------------------------------------------------------------------
	# Segment intersection test
	# -------------------------------------------------------------------------
	@staticmethod
	def segments_intersect(a, b, c, d):
		def orient(p, q, r):
			return (q.x - p.x) * (r.y - p.y) - (q.y - p.y) * (r.x - p.x)

		o1 = orient(a, b, c)
		o2 = orient(a, b, d)
		o3 = orient(c, d, a)
		o4 = orient(c, d, b)

		# proper intersection
		if o1 * o2 < 0 and o3 * o4 < 0:
			return True

		return False

	# -------------------------------------------------------------------------
	# Ensure polygon lies completely on ONE SIDE of line AB
	# -------------------------------------------------------------------------
	@staticmethod
	def is_polygon_one_side(a, b, points, start_idx, end_idx):
		ax, ay = a.x, a.y
		bx, by = b.x, b.y

		side_sign = 0

		for i, p in enumerate(points):
			# skip points that define the edge itself
			if start_idx <= i <= end_idx:
				continue

			# compute cross product sign
			cross = (bx - ax) * (p.y - ay) - (by - ay) * (p.x - ax)

			if abs(cross) < 1e-9:
				continue  # practically on line

			sign = 1 if cross > 0 else -1

			if side_sign == 0:
				side_sign = sign  # first non-zero decides the side
			elif sign != side_sign:
				return False  # found point on other side → invalid edge

		return True

	@staticmethod
	def perpendicular_distance(P, A, B):
		# if A and B are the same point
		if A == B:
			return ((P.x - A.x)**2 + (P.y - A.y)**2)**0.5

		# |(B - A) × (A - P)| / |B - A|
		numerator = abs((B.x - A.x)*(A.y - P.y) - (B.y - A.y)*(A.x - P.x))
		denominator = ((B.x - A.x)**2 + (B.y - A.y)**2)**0.5
		return numerator / denominator
