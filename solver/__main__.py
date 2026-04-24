import sys

import cv2

from solver.debugger import Debugger
from solver.puzzle import Puzzle
from solver.uart_handler import UartHandler

UART_PORT = '/dev/ttyAMA4'

def prod():
	UartHandler(UART_PORT)

def test():
	Debugger.enable_log()
	UartHandler(UART_PORT)

def debug(path: str):
	Debugger.enable_log()
	Debugger.enable_plot()

	image = cv2.imread(path)

	if image is None:
		raise FileNotFoundError(f"Image not found: {path}")

	solution = Puzzle.solve(image)

	if solution is not None:
		Debugger.log("Uart messages:\n")
		for message in UartHandler.get_piece_messages(solution.pieces):
			Debugger.log(message)

if __name__ == "__main__":
	if len(sys.argv) >= 2:
		if (sys.argv[1] == '--test'):
			test()
		else:
			debug(sys.argv[1])
	else:
		prod()
