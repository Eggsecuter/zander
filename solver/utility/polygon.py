import numpy as np
import math

from typing import List
from solver.models.edge import Edge
from solver.models.vector2 import Vector2
from solver.utility.angle import Angle

class PolygonUtility:
	@staticmethod
	def roughen(points: List[Vector2], epsilon) -> List[Vector2]:
		'''
		Roughen shape to reduce points and improve further calculation performance.
		'''
		if len(points) < 3:
			return points

		# find point with max distance from line (points[0] -> points[-1])
		max_dist = 0
		index = 0

		for i in range(1, len(points) - 1):
			dist = PolygonUtility.__perpendicular_distance(points[i], points[0], points[-1])
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
		'''
		Calculate center of mass
		'''
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
	def detect_edges(points: List[Vector2], line_epsilon: float, min_length: float, corner_margin: float, corner_margin_radiants: float) -> List[Edge]:
		'''
		Detect all points which form a fairly straight line and can be placed against a wall without the rest of the shape colliding first.

		Criteria of a valid edge are:
		- They form a straight line
		- If extended infinitely, it should not collide with the rest of the polygon

		Args:
			points: Shape
			line_epsilon: Tolerance for straightness of a line
			min_length: Minimal length of an edge
			corner_margin: Tolerance for distance to last detected edge line
			corner_margin_radiants: Tolerance for angle to last detected edge line (ideally 90 degrees)
		'''
		if len(points) < 2:
			return []

		edges: List[Edge] = []
		point_count = len(points)
		start = 0

		while start < point_count:
			end = start + 1

			while True:
				segment = [points[i % point_count] for i in range(start, end + 1)]
				a = segment[0]
				b = segment[-1]

				# check collinearity
				if not all(PolygonUtility.__distance_point_to_line(p, a, b) <= line_epsilon
						for p in segment):
					break

				# check valid frame line
				if PolygonUtility.__line_intersects_polygon(a, b, points, start % point_count, end % point_count):
					break

				if not PolygonUtility.__is_polygon_one_side(a, b, points, start % point_count, end % point_count):
					break

				end += 1

				if end - start >= point_count:  # full circle reached
					break

			if end - start >= 2:
				end -= 1

				start_index = start % point_count
				end_index = end % point_count

				edge = Edge(points, [start_index, end_index])

				if edge.get_length() >= min_length:
					edges.append(edge)

			start = end

		current_combined_edge = None
		removal_edge_indices = []

		for index, edge in enumerate(edges):
			other_index = (index + 1) % len(edges)
			other = edges[other_index]

			if edge.end.distance_to(other.start) <= corner_margin and Angle.is_right_angle(edge.get_end_angle(), other.get_start_angle(), corner_margin_radiants):
				if current_combined_edge is None:
					current_combined_edge = edge

				current_combined_edge.point_indices.extend(other.point_indices[1:])
				removal_edge_indices.append(other_index)
			else:
				current_combined_edge = None

		# filter marked edges which got combined into an other
		edges = [edge for index, edge in enumerate(edges) if index not in removal_edge_indices]

		edges.sort(key=lambda edge: edge.get_length(), reverse=True)

		return [edges[0]]

	@staticmethod
	def __perpendicular_distance(P, A, B):
		# if A and B are the same point
		if A == B:
			return ((P.x - A.x)**2 + (P.y - A.y)**2)**0.5

		# |(B - A) × (A - P)| / |B - A|
		numerator = abs((B.x - A.x)*(A.y - P.y) - (B.y - A.y)*(A.x - P.x))
		denominator = ((B.x - A.x)**2 + (B.y - A.y)**2)**0.5
		return numerator / denominator

	# -------------------------------------------------------------------------
	# Point–line distance
	# -------------------------------------------------------------------------
	@staticmethod
	def __distance_point_to_line(p, a, b):
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
	def __line_intersects_polygon(a, b, points, start_idx, end_idx):
		n = len(points)

		for i in range(n):
			j = (i + 1) % n

			# skip edges of the current segment
			if start_idx <= end_idx:
				if start_idx - 1 <= i <= end_idx:
					continue
			else:  # wrap-around case
				if i >= start_idx - 1 or i <= end_idx:
					continue

			p1 = points[i]
			p2 = points[j]

			if PolygonUtility.__segments_intersect(a, b, p1, p2):
				return True

		return False

	# -------------------------------------------------------------------------
	# Segment intersection test
	# -------------------------------------------------------------------------
	@staticmethod
	def __segments_intersect(a, b, c, d):
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
	def __is_polygon_one_side(a, b, points, start_idx, end_idx):
		ax, ay = a.x, a.y
		bx, by = b.x, b.y

		side_sign = 0

		for i, p in enumerate(points):
			# skip points that define the edge itself
			if start_idx <= end_idx:
				if start_idx <= i <= end_idx:
					continue
			else:  # wrap-around
				if i >= start_idx or i <= end_idx:
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
