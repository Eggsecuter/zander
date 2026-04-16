from typing import List

from serial import Serial
from solver.logger import Logger
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
			Logger.log("Listening for messages...")

			# blocks until message arrives
			message = self.stream.readline()

			if message:
				decoded = message.decode('utf-8').strip()

				if decoded == 'ready':
					Logger.log("Received ready")
					self.__on_ready()
				elif decoded == 'error':
					Logger.log("Received error")
					self.__on_error()
				else:
					Logger.log(f"Received unknown message {decoded}")

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
		Logger.log("System abort triggered")

		# clear state
		self.messages = []

		# optionally flush serial buffers
		self.stream.reset_input_buffer()
		self.stream.reset_output_buffer()

		# restart listening loop
		self.listen()

	def __send(self, message: str):
		Logger.log(f"Sending {message}")
		self.stream.write(message.encode('utf-8'))

	def __solve(self):
		# TODO capture image
		image = None

		puzzle = Puzzle(image)
		pieces = puzzle.solve()

		if len(pieces) <= 0:
			return

		# create message list
		self.messages.append("reset\n")

		# TODO piece messages

		self.messages.append("finish\n")
