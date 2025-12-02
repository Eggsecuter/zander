class ResetMessage:
	def __init__(self, _start: bool):
		self.start = _start

	def get_type(self):
		return 'reset'

	def to_json(self):
		return f"{{\"start\": {str(self.start).lower()}}}"
