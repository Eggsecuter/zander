import numpy as np
from typing import List, cast
from shapely import Polygon
from shapely.geometry import LineString
from solver.debugger import Debugger
from solver.models.edge import Edge
from solver.models.piece import Piece


EDGE_SIMPLIFY_TOLERANCE = 10.0
MIN_EDGE_LENGTH = 100
POLYGON_INTERSECT_SHRINK_FACTOR = -10

class PieceDetector:
	@staticmethod
	def detect(polygons: List[Polygon]) -> List[Piece]:
		pieces = []

		for polygon in polygons:
			edges = PieceDetector.__extract_edges(polygon)
			pieces.append(Piece(polygon, edges))

			Debugger.log(f"Piece with {len(polygon.exterior.coords)} points has {len(edges)} edges")

		Debugger.log("\n")

		return pieces

	@staticmethod
	def __extract_edges(polygon: Polygon) -> List[Edge]:
		edges: List[Edge] = []

		simplified = polygon.simplify(EDGE_SIMPLIFY_TOLERANCE, preserve_topology=True)
		coords = list(cast(Polygon, simplified).exterior.coords)

		for i in range(len(coords) - 1):
			edge = Edge(LineString([coords[i], coords[i + 1]]), True)

			# flag invalid edges
			# matcher first tries to solve with only valid edges then with all
			if edge.length < MIN_EDGE_LENGTH or PieceDetector.__extend_line(edge.line).intersects(polygon.buffer(POLYGON_INTERSECT_SHRINK_FACTOR)):
				edge.is_frame_edge = False

			edges.append(edge)

		# sort for performance
		edges.sort(key=lambda edge: edge.length, reverse=True)

		return edges

	@staticmethod
	def __extend_line(line: LineString, scale: float = 1e6) -> LineString:
		p1, p2 = map(np.array, line.coords)

		direction = p2 - p1
		direction = direction / np.linalg.norm(direction)

		# extend both directions
		new_p1 = p1 - direction * scale
		new_p2 = p2 + direction * scale

		return LineString([new_p1, new_p2])
