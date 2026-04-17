import argparse
from pathlib import Path

from calibrate.aruco_generator import generate_markers
from calibrate.aruco_detector import detect_markers_from_camera
from calibrate.camera_calibration import take_photos_from_camera, calibrate_from_photos


def parse_size(value: str) -> tuple[int, int]:
    parts = value.lower().replace("*", "x").split("x")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError(f"Invalid size {value!r}: use WxH, e.g. 1920x1080")
    try:
        return (int(parts[0]), int(parts[1]))
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid size {value!r}: WxH must be integers") from e


def _run_generate_markers(_args) -> int:
    return generate_markers()


def _run_detect(args) -> int:
    return detect_markers_from_camera(
        use_calibration=not args.no_calibration,
        calibration_file=args.calibration,
    )


def _run_take_photos(args) -> int:
    return take_photos_from_camera(output_size=args.size)


def _run_calibrate(_args) -> int:
    return calibrate_from_photos()


COMMANDS = {
    "generate-markers": _run_generate_markers,
    "detect": _run_detect,
    "take-photos": _run_take_photos,
    "calibrate": _run_calibrate,
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="calibrate")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("generate-markers", help="Generate ArUco marker PNG files")

    detect = subparsers.add_parser("detect", help="Run live ArUco detection from camera")
    detect.add_argument(
        "--no-calibration",
        action="store_true",
        help="Skip camera.yml undistortion",
    )
    detect.add_argument(
        "--calibration",
        type=Path,
        default=Path("camera.yml"),
        help="Path to camera.yml (default: ./camera.yml)",
    )

    take = subparsers.add_parser(
        "take-photos",
        help="Take chessboard photos for calibration (every 2s)",
    )
    take.add_argument(
        "--size",
        metavar="WxH",
        type=parse_size,
        default=None,
        help="Frame size e.g. 1920x1080. Default: full sensor resolution (Picamera2).",
    )

    subparsers.add_parser("calibrate", help="Calibrate camera from saved chessboard photos")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    return COMMANDS[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
