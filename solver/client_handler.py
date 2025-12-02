import json
import math
from dataclasses import asdict
from typing import List

from solver.solver import Solver
from solver.messages.camera import CameraMessage
from solver.messages.move import MoveMessage
from solver.messages.ready import ReadyMessage
from solver.messages.reset import ResetMessage

class ClientHandler:
	moves: List[MoveMessage] = []

	def __init__(self, reader, writer):
		self.reader = reader
		self.writer = writer
		self.address = writer.get_extra_info('peername')

		print(f"Connected: {self.address}")

	async def run(self):
		while True:
			try:
				line = await self.reader.readline()

				if not line:
					break

				type_name, body = line[4:].decode('utf-8').strip().split('=', 1)

				match type_name:
					case 'camera':
						message = CameraMessage.from_json(body)
						await self.analyze_puzzle(message)
					case 'ready':
						message = ReadyMessage.from_json(body)
						await self.next_move(message)
			except (ConnectionResetError, json.JSONDecodeError):
				continue

		print(f"Disconnected: {self.address}")
		self.writer.close()
		await self.writer.wait_closed()

	async def analyze_puzzle(self, message: CameraMessage):
		print(f"Camera image received: {message.data[:100]} ...]")

		self.moves = []

		main = Solver()
		main.load_image_from_buffer(message.data)
		pieces = main.run()

		print('\nAssembly Sequence for Robot:')
		print('='*60)
		for piece in pieces:
			radiants = piece.place_transform.rotation_radiant
			degrees = 180 * abs(radiants) / math.pi

			if radiants < 0:
				degrees = 360 - degrees

			message = MoveMessage(piece.center_of_mass.x,
				piece.center_of_mass.y,
				piece.place_transform.position.x,
				piece.place_transform.position.y,
				degrees
			)

			print(message.to_json())
			self.moves.append(message)

		print('='*60)

		await self.send_message(ResetMessage(True))

	async def next_move(self, _: ReadyMessage):
		print(f"Ready received moves left", len(self.moves))

		if len(self.moves) > 0:
			move = self.moves.pop(0)
			await self.send_message(move)
		else:
			await self.send_message(ResetMessage(False))

	async def send_message(self, message):
		self.writer.write((f"{message.get_type()}={message.to_json()}\n").encode())
		await self.writer.drain()
