class MoveMessage:
	def __init__(self, _grab_x: float, _grab_y: float, _place_x: float, _place_y: float, _rotation_degrees: float):
		self.grab_x = _grab_x
		self.grab_y = _grab_y
		self.place_x = _place_x
		self.place_y = _place_y
		self.rotation_degrees = _rotation_degrees

	def get_type(self):
		return 'move'

	def to_json(self):
		return f"{{\"grabX\": {self.grab_x}, \"grabY\": {self.grab_y}, \"placeX\": {self.place_x}, \"placeY\": {self.place_y}, \"rotationDegrees\": {self.rotation_degrees}}}"
