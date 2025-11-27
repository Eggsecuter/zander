import cv2
import base64
from solver.example.buffer_example import buffer
from solver.utility.image_loader import ImageLoader

class Main:
	def __init__(self):
		self.image = None

	def load_image_from_buffer(self, image_buffer: bytearray):
		self.image = ImageLoader.from_buffer(image_buffer)

	def load_image_from_path(self, image_path: str):
		self.image = ImageLoader.from_path(image_path)

	def run(self):
		if (self.image is None):
			print('No image loaded!')
			return

		cv2.imshow('Image', self.image)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

# Load image

# Threshold

# Filter

# Get contours

# Detect frame, pieces

# Get coordinates of grip points

# Detect piece outer edges (straight)

# For each corner combination (4 pieces -> 6 * 4 = 24 possibilities):
	# Place every corner piece
	# Calculate the needed transformation and rotation that the piece sits tightly in the frame, relative to the grip point

	# For each side combination (0 or 2 pieces -> 2 possibilities):
		# Place every side piece
		# Calculate the needed transformation and rotation that the piece sits tightly in the frame, relative to the grip point

		# Measure the overlap % inside the frame
		# Save the accuracy and the instructions for each piece to the result list

# Return the result with the best accuracy (least overlap %)

if __name__ == "__main__":
	main = Main()
	main.load_image_from_buffer(buffer)
	main.run()
