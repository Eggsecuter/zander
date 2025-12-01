import math

class Angle:
	@staticmethod
	def difference(a: float, b: float) -> float:
		"""
		Compute the shortest difference from angle a to angle b in radians.
		Result is in range [-pi, pi].

		Args:
			a (float): first angle in radians
			b (float): second angle in radians

		Returns:
			float: difference b - a in radians, wrapped to [-pi, pi]
		"""
		difference = (b - a) % (2 * math.pi) # wrap to [0, 2π)

		if difference > math.pi:
			difference -= 2 * math.pi # shift to [-π, π)

		return difference
