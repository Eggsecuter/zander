import ast
import json

class CameraMessage:
	data: bytearray

	def __init__(self, _data):
		self.data = _data

	@staticmethod
	def from_json(raw: str):
		parsed = json.loads(raw)

		return CameraMessage(bytearray(ast.literal_eval(parsed['data'])))
