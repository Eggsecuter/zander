from typing import List
from shapely import Polygon
from shapely.geometry import LineString
from solver.debugger import Debugger
from solver.models.piece import Piece

EDGE_SIMPLIFY_TOLERANCE = 10.0

class PieceDetector:
	@staticmethod
	def detect(polygons: List[Polygon]) -> List[Piece]:
		pieces = []

		for polygon in polygons:
			edges = PieceDetector._extract_edges(polygon)
			pieces.append(Piece(polygon, edges))

			Debugger.log(f"Piece with {len(polygon.exterior.coords)} points has {len(edges)} edges")

		Debugger.log("\n")

		return pieces

	@staticmethod
	def _extract_edges(polygon: Polygon) -> List[LineString]:
		edges = []
		coords = list(polygon.simplify(EDGE_SIMPLIFY_TOLERANCE).exterior.coords)

		for i in range(len(coords) - 1):
			edge = LineString([coords[i], coords[i + 1]])
			edges.append(edge)

		return edges
