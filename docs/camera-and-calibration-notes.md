# Kamera & Kalibrierung — Projektpunkte für die Dokumentation

Strukturierte Stichpunkte aus Git-Commits und Projektentwicklung (Kamera, Pi, Kalibrierung, ArUco).

---

## Architektur & Code-Organisation

- **`CameraService`** (`services/camera.py`): gemeinsame Kamera-API für **Picamera2** (Raspberry Pi) und **Fallback `cv2.VideoCapture`** (z. B. Entwicklung am Mac).
- **Kalibrierung** als eigenes Modul unter `calibrate/` (CLI: `generate-markers`, `take-photos`, `calibrate`, `detect`).
- **Trennung von „lib“ vs. „Service“**: Kamera-Integration als **Service** (Hardware-/Lifecycle-Logik), nicht als lose Utils.

---

## Raspberry Pi / Python-Umgebung

- **`picamera2`** kommt typischerweise über **`apt`** (`python3-picamera2`); **nicht** zuverlässig in `pyproject.toml` pinbar (Linux-only Abhängigkeiten wie `python-prctl`).
- **`uv` + venv**: System-Python nutzen (`/usr/bin/python3`) und **`uv venv --system-site-packages`**, damit das venv die **apt-installierten** Pakete (z. B. Picamera2) sieht — sonst fällt der Code auf V4L2/`VideoCapture` zurück.
- **`requires-python`**: an die **tatsächliche** Pi-Python-Version anpassen (z. B. 3.13), damit uv nicht ein eigenes 3.14+ herunterlädt und System-Pakete „verliert“.

---

## Kamera & Bildqualität

- **Pi Camera Module 3 Wide / NoIR**: Weitwinkel → **Rational Model** bei `calibrateCamera` (`CALIB_RATIONAL_MODEL`), mehr/gute Kalibrierbilder, Schachbrett auch in **Ecken/Ränder** des Bildes.
- **Autofokus**: für reproduzierbare Kalibrierung **manuell** (`AfMode` manual, `LensPosition` für **20 cm** Abstand Sensor–Arbeitsfläche → Dioptrien `1/0.20 = 5.0`; Parameter `lens_position` in `CameraService`).
- **Kalibrierumfang**: ausreichend Schachbrett-Fotos über dem **A4-Bereich (+ Reserve)** für Puzzleteil-Erkennung; keine Kalibrierung über die gesamte frühere Tischfläche nötig — wichtig sind weiterhin **gute Winkelabdeckung** und **Ecken/Ränder** im Bild für die Weitwinkel-Entzerrung.
- **Farbkanäle**: Picamera2/`capture_array` oft **RGB-Reihenfolge**, OpenCV erwartet **BGR** → Option **`picamera_rgb_buffer`** (RGB→BGR), sonst „blaue Haut“ in der Vorschau.
- **Headless vs. GUI**: **`opencv-contrib-python-headless`** vermeidet Qt-Display-Probleme über SSH; **mit VNC/Desktop** kann **`opencv-contrib-python`** (mit GUI) für `imshow` sinnvoll sein.
- **Auflösung / Sensor**: Standard **Still-Konfiguration** (Picamera2, bessere Qualität als reine Preview-Pipeline) mit **BGR888**, konfigurierbare **Ausgabegröße** (`use_still_configuration=False` → Preview), optional **quadratischer Crop** (`square_crop`) für einheitliches Seitenverhältnis.

---

## Kalibrierungs-Workflow

- **Schachbrett**: innere Eckpunkte (z. B. 9×6), **Feldgröße in Metern** (`SQUARE_SIZE`) muss zum Druck passen.
- **Fotos**: `take-photos` — Intervall (z. B. 3 s), **automatisches Ende** nach N Bildern, **Ordner vorher leeren**, Kalibrierfotos per **`.gitignore`** nicht ins Repo.
- **Ausgabe**: `camera.yml` im **Projektroot** mit **`matrix`**, **`new_matrix`**, **`distortion_coef`**, **`calibration_size`** (für Skalierung bei anderer Live-Auflösung).
- **Re-Projection Error** als Qualitätsmaß nach der Kalibrierung.
- **Live-Nutzung der Kalibrierung**: `detect` lädt `camera.yml` und wendet **`undistort`** vor der ArUco-Erkennung an (CLI: `--no-calibration`, `--calibration`).

---

## Betrieb / Fehlerbilder (Lessons Learned)

- **V4L2-Timeout / leeres `imshow`**: meist **kein Picamera2 im venv** → System-Python + `system-site-packages` oder `picamera2` via apt.
- **dpkg unterbrochen** auf dem Pi: Kernel-Updates/`initramfs` können SSH abbrechen; **screen**/**nohup** oder `dpkg --configure -a` mit stabiler Session.
- **Bugfix**: `zip(corners, ids.flatten())` statt `zip[tuple](...)` in der Marker-Schleife.

---

## Nächste Schritte (aus Tutorial / Planung)

- **Homographie / Perspektivkorrektur** (4 Eck-Marker → Weltkoordinaten) als logischer Schritt nach Kalibrierung.
- **Pose-Estimation** mit `estimatePoseSingleMarkers` nutzt dieselben intrinsischen Werte wie in `camera.yml`.

---

## OpenCV ArUco-API

- Es wird **`cv2.aruco.ArucoDetector`** (OpenCV contrib ≥ 4.7) verwendet — keine Legacy-`detectMarkers`-Funktion.

---

## Verwandte Dokumentation im Repo

- **`docs/camera-calibration.md`**: CLI, Parameter, Pi-Setup, YAML-Inhalt, `detect` mit Entzerrung.
