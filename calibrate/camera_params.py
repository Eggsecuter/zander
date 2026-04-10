"""Load camera.yml and apply lens undistortion (uses calibration from chessboard step)."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

DEFAULT_CALIBRATION_FILE = Path("camera.yml")


def scale_camera_matrix(
    mtx: np.ndarray,
    old_wh: tuple[int, int],
    new_wh: tuple[int, int],
) -> np.ndarray:
    """Scale intrinsics when image size differs from calibration resolution."""
    w_old, h_old = old_wh
    w_new, h_new = new_wh
    sx = w_new / w_old
    sy = h_new / h_old
    m = mtx.copy()
    m[0, 0] *= sx
    m[1, 1] *= sy
    m[0, 2] *= sx
    m[1, 2] *= sy
    return m


def load_camera_calibration(
    path: Path = DEFAULT_CALIBRATION_FILE,
) -> tuple[np.ndarray, np.ndarray, tuple[int, int] | None] | None:
    """
    Returns (camera_matrix, dist_coeffs, calibration_size_wh or None) or None if missing/invalid.
    calibration_size_wh is (width, height) of chessboard images; if None, assume live resolution matches calibration.
    """
    if not path.is_file():
        return None
    fs = cv2.FileStorage(str(path), cv2.FILE_STORAGE_READ)
    mtx = fs.getNode("matrix").mat()
    dist = fs.getNode("distortion_coef").mat()
    size_node = fs.getNode("calibration_size")
    fs.release()

    if mtx is None or dist is None or mtx.size == 0 or dist.size == 0:
        return None

    calib_wh: tuple[int, int] | None = None
    sz = size_node.mat()
    if sz is not None and sz.size >= 2:
        calib_wh = (int(sz.flat[0]), int(sz.flat[1]))

    return mtx, dist, calib_wh


def undistort_bgr_frame(
    frame: np.ndarray,
    mtx: np.ndarray,
    dist: np.ndarray,
    calib_wh: tuple[int, int] | None,
) -> np.ndarray:
    """Undistort a BGR frame; scales intrinsics if resolution != calibration."""
    h, w = frame.shape[:2]
    eff_calib = calib_wh if calib_wh is not None else (w, h)
    if (w, h) != eff_calib:
        mtx = scale_camera_matrix(mtx, eff_calib, (w, h))
    new_mtx, _roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
    return cv2.undistort(frame, mtx, dist, None, new_mtx)
