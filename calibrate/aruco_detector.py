from typing import Any

import cv2
import numpy as np
import cv2.aruco as aruco

DICT = aruco.DICT_4X4_50
GROUP_A = [0, 1, 2, 3, 0]
GROUP_B = [4, 5, 7, 6, 4]

def build_centers_by_id(corners, ids):
	centers = {}
	for marker_corners, marker_id in zip[tuple](corners, ids.flatten()):
		pts = marker_corners.reshape(4, 2)
		center = pts.mean(axis=0).astype(int)
		centers[int(marker_id)] = (int(center[0]), int(center[1]))
	return centers

def draw_marker_path(display, centers_by_id, path_ids, color=(0, 255, 255), thickness=3):
	for a, b in zip(path_ids, path_ids[1:]):
		if a in centers_by_id and b in centers_by_id:
			cv2.line(display, centers_by_id[a], centers_by_id[b], color, thickness)

def draw_workspace_paths(display, corners, ids):
	if ids is None or len(ids) == 0:
		return display

	centers_by_id = build_centers_by_id(corners, ids)

	# optional: Zentren + ID labels zeichnen
	for marker_id, (x, y) in centers_by_id.items():
		cv2.circle(display, (x, y), 5, (255, 255, 0), -1)
		cv2.putText(display, f"{marker_id}", (x + 8, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2, cv2.LINE_AA)

	# Gruppe A + B
	draw_marker_path(display, centers_by_id, GROUP_A, color=(0, 255, 255), thickness=3)
	draw_marker_path(display, centers_by_id, GROUP_B, color=(255, 0, 255), thickness=3)

	return display

def detect_from_camera(camera_index: int = 0) -> int:
	cap = cv2.VideoCapture(camera_index)
	if not cap.isOpened():
		raise RuntimeError(f"Could not open camera {camera_index}")

	aruco_dict = aruco.getPredefinedDictionary(DICT)
	params = aruco.DetectorParameters()

	while True:
		ret, frame = cap.read()
		if not ret:
			break

		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		corners, ids, _ = aruco.detectMarkers(gray, aruco_dict, parameters=params)

		display = frame.copy()
		if ids is not None and len(ids) > 0:
			display = aruco.drawDetectedMarkers(display, corners, ids)
			display = draw_workspace_paths(display, corners, ids)

		cv2.imshow("Aruco Detect", display)
		if cv2.waitKey(1) & 0xFF == ord("q"):
			break

	cap.release()
	cv2.destroyAllWindows()
	return 0