from pathlib import Path
import cv2
import cv2.aruco as aruco

OUT_DIR = Path("data/calibration/markers")
DICT = aruco.DICT_4X4_50
COUNT = 8
SIZE_PX = 500
BORDER_BITS = 1

def generate_markers() -> int:
	dictionary = aruco.getPredefinedDictionary(DICT)
	OUT_DIR.mkdir(parents=True, exist_ok=True)

	for marker_id in range(COUNT):
		image = aruco.generateImageMarker(dictionary, marker_id, SIZE_PX, borderBits=BORDER_BITS)
		out_path = OUT_DIR / f"aruco_marker_{marker_id}.png"
		if not cv2.imwrite(str(out_path), image):
			raise RuntimeError(f"Could not write marker to {out_path}")
		print(f"saved: {out_path}")

	return 0