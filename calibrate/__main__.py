import argparse

from calibrate.aruco_generator import generate_markers
from calibrate.aruco_detector import detect_markers_from_camera
from calibrate.camera_calibration import take_photos_from_camera, calibrate_from_photos

def main() -> int:
	parser = argparse.ArgumentParser(prog="calibrate")
	subparsers = parser.add_subparsers(dest="command", required=True)

	subparsers.add_parser("generate-markers", help="Generate ArUco marker PNG files")
	subparsers.add_parser("detect", help="Run live ArUco detection from camera")
	subparsers.add_parser("take-photos", help="Take chessboard photos for calibration (every 2s)")
	subparsers.add_parser("calibrate", help="Calibrate camera from saved chessboard photos")

	args = parser.parse_args()

	if args.command == "generate-markers":
		return generate_markers()

	if args.command == "detect":
		return detect_markers_from_camera()

	if args.command == "take-photos":
		return take_photos_from_camera()

	if args.command == "calibrate":
		return calibrate_from_photos()

	parser.print_help()
	return 1

if __name__ == "__main__":
	raise SystemExit(main())
