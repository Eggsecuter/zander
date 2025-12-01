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

	@staticmethod
	def is_right_angle(angle1, angle2, margin):
		# normalize angles to [0, 2*pi)
		a1 = angle1 % (2 * math.pi)
		a2 = angle2 % (2 * math.pi)

		# target: 90° CCW from angle1
		target = (a1 + math.pi/2) % (2 * math.pi)

		# compute smallest angular difference
		difference = (a2 - target + math.pi) % (2 * math.pi) - math.pi

		return abs(difference) <= margin
