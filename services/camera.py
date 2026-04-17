import numpy as np

import cv2

# Raspberry Pi Camera Module 3 (IMX708): wide and standard share the same 12.3 MP sensor.
# Picamera2's ``sensor_resolution`` matches this; use as explicit ``output_size`` if you want
# a documented choice instead of ``None``.
RPI_CAMERA_MODULE3_IMX708_MAX_SIZE: tuple[int, int] = (4608, 2592)


class CameraService:
    """
    Abstracts camera access: uses Picamera2 on Raspberry Pi,
    falls back to cv2.VideoCapture for local development.

    Uses **still** configuration by default (``create_still_configuration``): ISP tuned for
    photo-style captures (e.g. higher noise reduction quality vs preview). Pass
    ``use_still_configuration=False`` for ``create_preview_configuration`` if you need higher FPS.

    Pass ``output_size=None`` to use Picamera2's ``sensor_resolution`` (for Camera Module 3 /
    IMX708 typically **4608×2592**, same as :data:`RPI_CAMERA_MODULE3_IMX708_MAX_SIZE`).
    That is the sharpest main stream; higher CPU/RAM use than 1080p.
    ``camera_params.undistort_bgr_frame`` scales intrinsics when the live frame size differs
    from ``camera.yml``.
    """

    def __init__(
        self,
        index: int = 0,
        output_size: tuple[int, int] | None = (1920, 1080),
        square_crop: bool = False,
        *,
        use_still_configuration: bool = True,
        lens_position: float = 4.347826087,
        picamera_rgb_buffer: bool = True,
        exposure_value: float | None = 1.09,
        ae_metering: str | None = "spot",
    ):
        self._index = index
        # None = use full sensor resolution (Picamera2); sharpest, more CPU/RAM than 1080p.
        self._output_size = output_size
        self._square_crop = square_crop
        self._lens_position = lens_position
        self._picamera_rgb_buffer = picamera_rgb_buffer
        self._exposure_value = exposure_value
        self._ae_metering = ae_metering
        self._use_still_configuration = use_still_configuration
        self._cam = None
        self._fallback = False
        self._configured_main_size: tuple[int, int] | None = None

    def open(self, lock_focus: bool = True) -> None:
        try:
            from picamera2 import Picamera2
            from libcamera import controls

            self._cam = Picamera2()
            sensor_res = self._cam.sensor_resolution
            main_size = self._output_size if self._output_size is not None else sensor_res

            stream_kw = dict(
                main={
                    "format": "BGR888",
                    "size": main_size,
                },
                raw={
                    "size": sensor_res,
                },
                buffer_count=2,
            )
            if self._use_still_configuration:
                config = self._cam.create_still_configuration(**stream_kw)
            else:
                config = self._cam.create_preview_configuration(**stream_kw)
            self._cam.configure(config)
            try:
                main_cfg = self._cam.stream_configuration("main")
                sz = main_cfg["size"]
                self._configured_main_size = (int(sz[0]), int(sz[1]))
            except (KeyError, TypeError, IndexError, ValueError):
                self._configured_main_size = None
            self._cam.start()

            ctrl: dict = {}
            if lock_focus:
                ctrl.update({
                    "AfMode": controls.AfModeEnum.Manual,
                    # Dioptrien ≈ 1 / Abstand_sensor_zur_Arbeitsfläche_in_m (hier 20 cm → 5.0)
                    "LensPosition": self._lens_position,
                })
            if self._exposure_value is not None:
                ctrl["ExposureValue"] = float(self._exposure_value)
            if self._ae_metering is not None:
                metering = self._ae_metering.strip().lower()
                modes = {
                    "centre": controls.AeMeteringModeEnum.CentreWeighted,
                    "center": controls.AeMeteringModeEnum.CentreWeighted,
                    "spot": controls.AeMeteringModeEnum.Spot,
                    "average": controls.AeMeteringModeEnum.Matrix,
                    "matrix": controls.AeMeteringModeEnum.Matrix,
                }
                if metering not in modes:
                    raise ValueError(
                        f"ae_metering must be one of {sorted(modes)!r}, got {self._ae_metering!r}"
                    )
                ctrl["AeMeteringMode"] = modes[metering]
            if ctrl:
                self._cam.set_controls(ctrl)

            self._fallback = False

        except (ImportError, Exception):
            self._cam = cv2.VideoCapture(self._index)
            if not self._cam.isOpened():
                raise RuntimeError(f"Could not open camera {self._index}")
            if self._output_size is not None:
                self._cam.set(cv2.CAP_PROP_FRAME_WIDTH, self._output_size[0])
                self._cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self._output_size[1])
            self._fallback = True
            self._configured_main_size = None

    @property
    def configured_main_size(self) -> tuple[int, int] | None:
        """``(width, height)`` of the main stream after ``open()``, or ``None`` (fallback / not opened)."""
        return self._configured_main_size

    def read(self) -> tuple[bool, np.ndarray]:
        """Returns (success, frame) — same interface as cv2.VideoCapture.read()."""
        if self._fallback:
            ok, frame = self._cam.read()
        else:
            frame = self._cam.capture_array()
            ok = True
            # Trotz "BGR888" liefert Picamera2 oft RGB-Reihenfolge → Haut wirkt bläulich in OpenCV (BGR).
            if self._picamera_rgb_buffer:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

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
        self._configured_main_size = None

    def __enter__(self) -> "CameraService":
        self.open()
        return self

    def __exit__(self, *_) -> None:
        self.release()
