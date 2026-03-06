import argparse

from calibrate.aruco_generator import generate_markers

def main() -> int:
	parser = argparse.ArgumentParser(prog="calibrate")
	subparsers = parser.add_subparsers(dest="command", required=True)

	subparsers.add_parser("generate-markers", help="Generate ArUco marker PNG files")

	args = parser.parse_args()

	if args.command == "generate-markers":
		return generate_markers()

	parser.print_help()
	return 1


if __name__ == "__main__":
	raise SystemExit(main())