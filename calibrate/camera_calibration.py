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
) -> int:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    last_recorded_time = time.time()
    frame_count = 0

    print(f"Saving {max_photos} photos to '{output_dir}' every {interval}s. Press 'q' to stop early.")

    with CameraService() as cam:
        while frame_count < max_photos:
            _, frame = cam.read()
            curr_time = time.time()
            if curr_time - last_recorded_time >= interval:
                path = output_dir / f"frame_{frame_count:03d}.png"
                cv2.imwrite(str(path), frame)
                print(f"  [{frame_count + 1}/{max_photos}] Saved {path}")
                last_recorded_time = curr_time
                frame_count += 1
    print(f"Done. {frame_count} photos saved.")
    return 0


def calibrate_from_photos(photos_dir: Path = PHOTOS_DIR, output_dir: Path = OUTPUT_DIR, calibration_file: Path = CALIBRATION_FILE) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    calibration_file.parent.mkdir(parents=True, exist_ok=True)

    objp = np.zeros((GRID[0] * GRID[1], 3), np.float32)
    objp[:, :2] = (SQUARE_SIZE * np.mgrid[0 : GRID[0], 0 : GRID[1]]).T.reshape(-1, 2)

    objpoints: list[np.ndarray] = []
    imgpoints: list[np.ndarray] = []

    images = sorted(glob.glob(str(photos_dir / "*.png")))
    if not images:
        print(f"No PNG images found in '{photos_dir}'.")
        return 1

    gray = None
    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(gray, GRID, CHESSBOARD_FLAGS)
        if not ret:
            print(f"  Skipped (no chessboard found): {fname}")
            continue

        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), CRITERIA)
        imgpoints.append(corners2)

        print(f"  Detected: {fname}")

    if len(objpoints) < 5:
        print(f"Not enough valid images ({len(objpoints)}). Need at least 5.")
        return 1

    print(f"\nCalibrating with {len(objpoints)} images...")
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray.shape[::-1], None, None,
        flags=cv2.CALIB_RATIONAL_MODEL,
    )

    # Undistort all images and save
    for i, fname in enumerate([f for f in images if _has_corners(f, GRID, CHESSBOARD_FLAGS)]):
        img = cv2.imread(fname)
        h, w = img.shape[:2]
        new_mtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
        dst = cv2.undistort(img, new_mtx, dist, None, new_mtx)
        out_path = output_dir / f"{i:03d}.png"
        cv2.imwrite(str(out_path), dst)

    # Save camera matrix and distortion coefficients
    cv_file = cv2.FileStorage(str(calibration_file), cv2.FILE_STORAGE_WRITE)
    cv_file.write("new_matrix", new_mtx)
    cv_file.write("distortion_coef", dist)
    cv_file.release()

    # Re-projection error
    total_error = 0.0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        total_error += cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)

    mean_error = total_error / len(objpoints)
    print(f"Calibration saved to '{calibration_file}'")
    print(f"Re-projection error: {mean_error:.6f} (lower is better)")
    return 0


def _has_corners(fname: str, grid: tuple[int, int], flags: int) -> bool:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, _ = cv2.findChessboardCorners(gray, grid, flags)
    return ret
