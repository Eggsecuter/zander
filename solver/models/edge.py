
import math
from shapely import LineString


class Edge:
	@property
	def startX(self) -> float:
		return self.line.coords[0][0]

	@property
	def startY(self) -> float:
		return self.line.coords[0][1]

	@property
	def endX(self) -> float:
		return self.line.coords[-1][0]

	@property
	def endY(self) -> float:
		return self.line.coords[-1][1]

	@property
	def length(self) -> float:
		return self.line.length

	@property
	def angle_degrees(self) -> float:
		# current angle of the edge (degrees)
		return math.degrees(math.atan2(self.endY - self.startY, self.endX - self.startX))

	def __init__(self, line: LineString, is_frame_edge: bool):
		self.line = line
		self.is_frame_edge = is_frame_edge
