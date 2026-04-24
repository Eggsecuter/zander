"""ArUco live detection — requires OpenCV contrib >= 4.7 (cv2.aruco.ArucoDetector)."""

from pathlib import Path

import cv2
import cv2.aruco as aruco

from calibrate.camera_params import load_camera_calibration, undistort_bgr_frame
from services.camera import CameraService

DICT = aruco.DICT_4X4_50

# (path_marker_ids, BGR color) — each path is drawn as a polyline between marker centers.
PATHS: list[tuple[list[int], tuple[int, int, int]]] = [
    ([0, 1, 2, 3, 0], (0, 255, 255)),
    ([4, 5, 7, 6, 4], (255, 0, 255)),
]


def build_centers_by_id(corners, ids) -> dict[int, tuple[int, int]]:
    centers: dict[int, tuple[int, int]] = {}
    for marker_corners, marker_id in zip(corners, ids.flatten()):
        pts = marker_corners.reshape(4, 2)
        cx, cy = pts.mean(axis=0).astype(int)
        centers[int(marker_id)] = (int(cx), int(cy))
    return centers


def draw_marker_path(display, centers_by_id, path_ids, color=(0, 255, 255), thickness=3):
    for a, b in zip(path_ids, path_ids[1:]):
        if a in centers_by_id and b in centers_by_id:
            cv2.line(display, centers_by_id[a], centers_by_id[b], color, thickness)


def draw_workspace_paths(display, corners, ids):
    if ids is None or len(ids) == 0:
        return display

    centers_by_id = build_centers_by_id(corners, ids)

    for marker_id, (x, y) in centers_by_id.items():
        cv2.circle(display, (x, y), 5, (255, 255, 0), -1)
        cv2.putText(
            display,
            f"{marker_id}",
            (x + 8, y - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2,
            cv2.LINE_AA,
        )

    for path_ids, color in PATHS:
        draw_marker_path(display, centers_by_id, path_ids, color=color, thickness=3)

    return display


def _load_calibration_if_enabled(use_calibration: bool, calibration_file: Path | None):
    if not use_calibration or calibration_file is None:
        return None
    calib = load_camera_calibration(calibration_file)
    if calib is not None:
        print(f"Using lens calibration from '{calibration_file}'")
    else:
        print(f"No valid calibration at '{calibration_file}' — running without undistort")
    return calib


def _process_frame(frame, detector, calib):
    if calib is not None:
        mtx, dist, calib_wh = calib
        frame = undistort_bgr_frame(frame, mtx, dist, calib_wh)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = detector.detectMarkers(gray)

    display = frame.copy()
    if ids is not None and len(ids) > 0:
        display = aruco.drawDetectedMarkers(display, corners, ids)
        display = draw_workspace_paths(display, corners, ids)
    return display


DISPLAY_MAX_WIDTH = 1600


def _fit_for_display(frame, max_width: int = DISPLAY_MAX_WIDTH):
    h, w = frame.shape[:2]
    if w <= max_width:
        return frame
    scale = max_width / w
    return cv2.resize(frame, (max_width, int(h * scale)), interpolation=cv2.INTER_AREA)


def detect_markers_from_camera(
    output_size: tuple[int, int] | None = None,
    square_crop: bool = False,
    calibration_file: Path | None = Path("camera.yml"),
    use_calibration: bool = True,
) -> int:
    """ArUco detection on full-sensor still captures. Loads camera.yml for lens undistortion."""
    calib = _load_calibration_if_enabled(use_calibration, calibration_file)

    aruco_dict = aruco.getPredefinedDictionary(DICT)
    detector = aruco.ArucoDetector(aruco_dict, aruco.DetectorParameters())

    with CameraService(
        output_size=output_size,
        square_crop=square_crop,
    ) as cam:
        while True:
            _, frame = cam.read()
            display = _process_frame(frame, detector, calib)
            cv2.imshow("Aruco Detect", _fit_for_display(display))
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()
    return 0
