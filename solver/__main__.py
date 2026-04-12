import sys

from solver.example.buffer_example import buffer
from solver.solver import Solver
from solver.uart_handler import UartHandler

UART_PORT = '/dev/tty.AMA4'

def main():
	UartHandler(UART_PORT)

def main_debug():
	main = Solver(True)
	main.load_image_from_path('./data/testing/1.png')
	main.run()

if __name__ == "__main__":
	debug = False

	if len(sys.argv) >= 2:
		if sys.argv[1] == '--debug':
			debug = True

	if debug:
		main_debug()
	else:
		main()
