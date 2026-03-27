import numpy as np


class CameraService:
    """
    Abstracts camera access: uses Picamera2 on Raspberry Pi,
    falls back to cv2.VideoCapture for local development.
    """

    def __init__(self, index: int = 0, output_size: tuple[int, int] = (1920, 1080), square_crop: bool = False):
        self._index = index
        self._output_size = output_size
        self._square_crop = square_crop
        self._cam = None
        self._fallback = False

    def open(self, lock_focus: bool = True) -> None:
        try:
            from picamera2 import Picamera2
            from libcamera import controls

            self._cam = Picamera2()
            sensor_res = self._cam.sensor_resolution

            config = self._cam.create_preview_configuration(
                main={
                    "format": "BGR888",
                    "size": self._output_size,
                },
                raw={
                    "size": sensor_res,
                },
                buffer_count=2,
            )
            self._cam.configure(config)
            self._cam.start()

            if lock_focus:
                self._cam.set_controls({
                    "AfMode": controls.AfModeEnum.Manual,
                    "LensPosition": 8.3,
                })

            self._fallback = False

        except (ImportError, Exception):
            import cv2
            self._cam = cv2.VideoCapture(self._index)
            if not self._cam.isOpened():
                raise RuntimeError(f"Could not open camera {self._index}")
            self._fallback = True

    def read(self) -> tuple[bool, np.ndarray]:
        """Returns (success, frame) — same interface as cv2.VideoCapture.read()."""
        if self._fallback:
            ok, frame = self._cam.read()
        else:
            frame = self._cam.capture_array()
            ok = True

        if ok and self._square_crop:
            frame = self._crop_square(frame)

        return ok, frame

    @staticmethod
    def _crop_square(frame: np.ndarray) -> np.ndarray:
        """Crops the center square from a frame."""
        h, w = frame.shape[:2]
        if w > h:
            x = (w - h) // 2
            return frame[:, x:x + h]
        elif h > w:
            y = (h - w) // 2
            return frame[y:y + w, :]
        return frame

    def release(self) -> None:
        if self._cam is None:
            return
        if self._fallback:
            self._cam.release()
        else:
            self._cam.stop()
        self._cam = None

    def __enter__(self) -> "CameraService":
        self.open()
        return self

    def __exit__(self, *_) -> None:
        self.release()
