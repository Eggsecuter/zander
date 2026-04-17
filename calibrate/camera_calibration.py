import cv2
import glob
import shutil
import time
import numpy as np
from pathlib import Path

from services.camera import CameraService

PHOTOS_DIR = Path("data/calibration/photos")
OUTPUT_DIR = Path("data/calibration/undistorted")
CALIBRATION_FILE = Path("camera.yml")

SQUARE_SIZE = 0.23  # meters
GRID = (9, 6)       # interior corner points (cols, rows)

CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
CHESSBOARD_FLAGS = cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE


def take_photos_from_camera(
    output_dir: Path = PHOTOS_DIR,
    max_photos: int = 25,
    interval: float = 3.0,
    output_size: tuple[int, int] | None = None,
) -> int:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    last_recorded_time = time.time()
    frame_count = 0

    print(f"Saving {max_photos} photos to '{output_dir}' every {interval}s. Press 'q' to stop early.")

    # output_size None = full sensor (Picamera2); pass e.g. (1920, 1080) for smaller/faster captures.
    with CameraService(output_size=output_size) as cam:
        logged_size = False
        while frame_count < max_photos:
            _, frame = cam.read()
            if not logged_size:
                h, w = frame.shape[:2]
                print(f"  Resolution: {w}x{h}.")
                logged_size = True
            curr_time = time.time()
            if curr_time - last_recorded_time >= interval:
                path = output_dir / f"frame_{frame_count:03d}.png"
                cv2.imwrite(str(path), frame)
                print(f"  [{frame_count + 1}/{max_photos}] Saved {path}")
                last_recorded_time = curr_time
                frame_count += 1
    print(f"Done. {frame_count} photos saved.")
    return 0


def _build_object_points() -> np.ndarray:
    objp = np.zeros((GRID[0] * GRID[1], 3), np.float32)
    objp[:, :2] = (SQUARE_SIZE * np.mgrid[0 : GRID[0], 0 : GRID[1]]).T.reshape(-1, 2)
    return objp


def _find_chessboard_points(
    images: list[str],
) -> tuple[list[str], list[np.ndarray], list[np.ndarray], tuple[int, int] | None]:
    """Detect chessboard corners once; returns (valid_filenames, objpoints, imgpoints, image_size)."""
    objp = _build_object_points()
    valid: list[str] = []
    objpoints: list[np.ndarray] = []
    imgpoints: list[np.ndarray] = []
    image_size: tuple[int, int] | None = None

    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, GRID, CHESSBOARD_FLAGS)
        if not ret:
            print(f"  Skipped (no chessboard found): {fname}")
            continue

        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), CRITERIA)
        valid.append(fname)
        objpoints.append(objp)
        imgpoints.append(corners2)
        image_size = gray.shape[::-1]  # (w, h)
        print(f"  Detected: {fname}")

    return valid, objpoints, imgpoints, image_size


def _write_undistorted(
    filenames: list[str],
    mtx: np.ndarray,
    dist: np.ndarray,
    output_dir: Path,
) -> None:
    for i, fname in enumerate(filenames):
        img = cv2.imread(fname)
        h, w = img.shape[:2]
        new_mtx, _roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
        dst = cv2.undistort(img, mtx, dist, None, new_mtx)
        cv2.imwrite(str(output_dir / f"{i:03d}.png"), dst)


def _save_calibration(
    calibration_file: Path,
    mtx: np.ndarray,
    dist: np.ndarray,
    image_size: tuple[int, int],
) -> None:
    w, h = image_size
    new_mtx, _roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
    fs = cv2.FileStorage(str(calibration_file), cv2.FILE_STORAGE_WRITE)
    fs.write("matrix", mtx)
    fs.write("new_matrix", new_mtx)
    fs.write("distortion_coef", dist)
    fs.write("calibration_size", np.array([[w, h]], dtype=np.int32))
    fs.release()


def _reprojection_error(
    objpoints: list[np.ndarray],
    imgpoints: list[np.ndarray],
    rvecs,
    tvecs,
    mtx: np.ndarray,
    dist: np.ndarray,
) -> float:
    total = 0.0
    for i in range(len(objpoints)):
        projected, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        total += cv2.norm(imgpoints[i], projected, cv2.NORM_L2) / len(projected)
    return total / len(objpoints)


def calibrate_from_photos(
    photos_dir: Path = PHOTOS_DIR,
    output_dir: Path = OUTPUT_DIR,
    calibration_file: Path = CALIBRATION_FILE,
) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    calibration_file.parent.mkdir(parents=True, exist_ok=True)

    images = sorted(glob.glob(str(photos_dir / "*.png")))
    if not images:
        print(f"No PNG images found in '{photos_dir}'.")
        return 1

    valid, objpoints, imgpoints, image_size = _find_chessboard_points(images)

    if len(objpoints) < 5 or image_size is None:
        print(f"Not enough valid images ({len(objpoints)}). Need at least 5.")
        return 1

    print(f"\nCalibrating with {len(objpoints)} images...")
    _, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, image_size, None, None,
        flags=cv2.CALIB_RATIONAL_MODEL,
    )

    _write_undistorted(valid, mtx, dist, output_dir)
    _save_calibration(calibration_file, mtx, dist, image_size)

    mean_error = _reprojection_error(objpoints, imgpoints, rvecs, tvecs, mtx, dist)
    print(f"Calibration saved to '{calibration_file}'")
    print(f"Re-projection error: {mean_error:.6f} (lower is better)")
    return 0
