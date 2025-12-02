import sys
import asyncio

from solver.client_handler import ClientHandler

HOST: str = '127.0.0.1'
PORT: int = 6048

async def handle_client(reader, writer):
	handler = ClientHandler(reader, writer)
	await handler.run()

async def main(port: int):
	server = await asyncio.start_server(handle_client, HOST, port, limit=10 * 1024 * 1024)
	address = ', '.join(str(socket.getsockname()) for socket in server.sockets)

	print(f"Serving on {address}")

	async with server:
		await server.serve_forever()

if __name__ == "__main__":
	port: int = PORT

	if len(sys.argv) >= 2 and sys.argv[1].isdigit():
		port = int(sys.argv[1])

	asyncio.run(main(port))
