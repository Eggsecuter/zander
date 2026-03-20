import argparse

from calibrate.aruco_generator import generate_markers
from calibrate.aruco_detector import detect_from_camera

def main() -> int:
	parser = argparse.ArgumentParser(prog="calibrate")
	subparsers = parser.add_subparsers(dest="command", required=True)

	subparsers.add_parser("generate-markers", help="Generate ArUco marker PNG files")
	subparsers.add_parser("detect", help="Run live ArUco detection from camera")

	args = parser.parse_args()

	if args.command == "generate-markers":
		return generate_markers()

	if args.command == "detect":
		return detect_from_camera()

	parser.print_help()
	return 1

if __name__ == "__main__":
	raise SystemExit(main())