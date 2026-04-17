from typing import List

from serial import Serial
from solver.constants import *
from solver.debugger import Debugger
from solver.puzzle import Puzzle


class UartHandler:
	stream: Serial
	messages: List[str] = []

	def __init__(self, port: str, baudrate: int = 115200):
		self.stream = Serial(port, baudrate)

		# wait for start
		self.listen()

	def listen(self):
		while True:
			Debugger.log("Listening for messages...")

			# blocks until message arrives
			message = self.stream.readline()

			if message:
				decoded = message.decode('utf-8').strip()

				if decoded == 'ready':
					Debugger.log("Received ready")
					self.__on_ready()
				elif decoded == 'error':
					Debugger.log("Received error")
					self.__on_error()
				else:
					Debugger.log(f"Received unknown message {decoded}")

	def __on_ready(self):
		if len(self.messages) <= 0:
			self.__solve()

		if len(self.messages) <= 0:
			self.__on_error()
			return

		message = self.messages.pop(0)
		self.__send(message)

		# listen to response
		self.listen()

	# restart the handler
	def __on_error(self):
		Debugger.log("System abort triggered")

		# clear state
		self.messages = []

		# optionally flush serial buffers
		self.stream.reset_input_buffer()
		self.stream.reset_output_buffer()

		# restart listening loop
		self.listen()

	def __send(self, message: str):
		Debugger.log(f"Sending {message}")
		self.stream.write(message.encode('utf-8'))

	def __solve(self):
		# TODO capture image
		image = None

		pieces = Puzzle.solve(image)

		if len(pieces) <= 0:
			return

		# create message list
		self.messages.append("reset\n")

		for piece in pieces:
			self.messages.append(
				f"move|x={int(piece.polygon.centroid.x)}|y={int(piece.polygon.centroid.y)}|rot=0\n"
			)
			self.messages.append(f"pick\n")
			# self.messages.append(
			# 	f"move|x={int(piece.placedPiece.polygon.centroid.x)}|y={int(piece.placedPiece.polygon.centroid.y)}|rot={int(piece.placedPiece.rotation * ROTATION_ACCURACY)}\n"
			# )
			self.messages.append(f"place\n")

		self.messages.append("finish\n")

		Debugger.log(self.messages)
