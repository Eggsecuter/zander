import time

from typing import List
from serial import Serial
from services.camera import CameraService
from solver.constants import *
from solver.debugger import Debugger
from solver.models.piece import Piece
from solver.puzzle import Puzzle


RESET_COMMAND = "reset"

class UartHandler:
	stream: Serial
	messages: List[str] = []

	@staticmethod
	def get_piece_messages(pieces: List[Piece]) -> List[str]:
		messages: List[str] = []

		for piece in pieces:
			if piece.placed_piece is None:
				continue

			messages.append(f"move|x={int(piece.polygon.centroid.y)}|y={int(piece.polygon.centroid.x)}|rot=0")
			messages.append("pick")

			# if piece.placed_piece is not None:
			# 	messages.append(f"move|x={int(piece.placed_piece.polygon.centroid.y)}|y={int(piece.placed_piece.polygon.centroid.x)}|rot={int(piece.placed_piece.rotation_degrees * ROTATION_ACCURACY)}")

			messages.append("place")

		return messages

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

		# if reset is remaining send it manually
		if len(self.messages) == 1 and self.messages[0] == RESET_COMMAND:
			time.sleep(1)
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
		self.stream.write(f"{message}\n".encode('utf-8'))

	def __solve(self):
		with CameraService() as cam:
			_, image = cam.read()
			Debugger.save_image(image)

		solution = Puzzle.solve(image)

		if solution is None:
			return

		# create message list
		self.messages.extend(UartHandler.get_piece_messages(solution.pieces))
		self.messages.append("finish")
		self.messages.append(RESET_COMMAND)

		Debugger.log(self.messages)
