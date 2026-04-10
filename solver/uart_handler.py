from serial import Serial
from solver.example.buffer_example import buffer
from solver.solver import Solver
from typing import List

class UartHandler:
	stream: Serial
	messages: List[str] = None

	def __init__(self, port: str):
		self.stream = Serial(port, 115200)

		# wait for initial ready (calibration finished)
		self.listen()

	def listen(self):
		while True:
			print("Listening for message...")

			# blocks until message arrives
			message = self.stream.readline()

			if message:
				decoded = message.decode('utf-8').strip()

				if decoded == 'ready':
					print("Received ready")
					self.on_ready()
					break
				elif decoded == 'error':
					print("Received error")
					self.on_error()
					break
				else:
					print(f"Received unknown message {decoded}")

	def on_ready(self):
		if self.messages != None and len(self.messages) <= 0:
			return

		if self.messages == None:
			if not self.solve():
				return

		message = self.messages.pop(0)
		self.send(message)

		# listen to response
		self.listen()

	# restart the handler
	def on_error(self):
		print("System abort triggered")

		# clear state
		self.messages = None

		# optionally flush serial buffers
		self.stream.reset_input_buffer()
		self.stream.reset_output_buffer()

		# restart listening loop
		self.listen()

	def send(self, message: str):
		print(f"Sending {message}")
		self.stream.write(message.encode('utf-8'))

	def solve(self) -> bool:
		solver = Solver()

		# TODO capture image from pi cam
		solver.load_image_from_buffer(buffer)

		pieces = solver.run()

		if len(pieces) <= 0:
			self.on_error()
			return False

		# create message list
		self.messages = ["reset\n"]

		for piece in pieces:
			self.messages.append(f"move|x={self.encode_float(piece.center_of_mass.x)}|y={self.encode_float(piece.center_of_mass.y)}|rot=0\n")
			self.messages.append(f"pick\n")
			self.messages.append(f"move|x={self.encode_float(piece.place_transform.position.x)}|y={self.encode_float(piece.place_transform.position.y)}|rot={self.encode_float(piece.place_transform.rotation_radiant)}\n")
			self.messages.append(f"place\n")

		self.messages.append("finish\n")

		return True

	def encode_float(self, value: float) -> str:
		# in micrometers
		return int(value * 1000)
