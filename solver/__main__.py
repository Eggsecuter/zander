import sys

import cv2

from solver.logger import Logger
from solver.puzzle import Puzzle
from solver.uart_handler import UartHandler

UART_PORT = '/dev/tty.AMA4'

def prod():
	UartHandler(UART_PORT)

def test():
	Logger.enable_logs()
	UartHandler(UART_PORT)

def debug(path: str):
	Logger.enable_logs()
	image = cv2.imread(path)

	if image is None:
		raise FileNotFoundError(f"Image not found: {path}")

	puzzle = Puzzle(image)
	puzzle.solve()

if __name__ == "__main__":
	if len(sys.argv) >= 2:
		if (sys.argv[1] == '--test'):
			test()
		else:
			debug(sys.argv[1])
	else:
		prod()
