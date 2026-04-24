# Camera Calibration

## Projektstruktur

```
zander2/
  services/
    camera.py             ← Hardware-Abstraktion für die Kamera
  calibrate/
    __main__.py           ← CLI-Einstiegspunkt
    aruco_detector.py     ← Live ArUco-Erkennung
    aruco_generator.py    ← ArUco Marker PNGs generieren
    camera_calibration.py ← Kalibrierungsworkflow
  data/
    calibration/
      photos/             ← Kalibrierfotos (Eingabe)
      undistorted/        ← Korrigierte Bilder (Ausgabe)
      markers/            ← Generierte ArUco PNGs
  camera.yml              ← Kalibrierungsresultat (Ausgabe)
```

---

## `services/camera.py` — CameraService

Abstrahiert den Kamerazugriff. Auf dem Raspberry Pi wird **Picamera2** verwendet, auf dem Mac fällt es automatisch auf **cv2.VideoCapture** zurück — ohne Codeänderungen.

### Fokus-Lock

`open()` akzeptiert einen `lock_focus: bool = True` Parameter. Ist er aktiv, wird der Autofokus des Pi Camera Module 3 auf manuell fixiert.

`LensPosition` ist in Dioptrien (`1 / Distanz_in_Meter`). Bei **20 cm** Abstand Sensor zur Arbeitsfläche (A4-Bereich + Reserve):

```
LensPosition = 1 / 0.20 = 5.0
```

Über `CameraService(lens_position=…)` anpassbar, falls sich der Abstand ändert.

> **Wichtig:** Der Wert muss identisch für Kalibrierung und Betrieb sein. Nur so stimmen die intrinsischen Parameter der `camera.yml` mit der tatsächlichen Aufnahmesituation überein.

### Parameter

| Parameter | Standard | Beschreibung |
|---|---|---|
| `index` | `0` | Kamera-Index (nur cv2-Fallback) |
| `output_size` | `(1920, 1080)` | Ausgabeauflösung; `None` = volle Sensorauflösung (Picamera2), mehr Pixel, höhere Last. Camera Module 3 (IMX708): typisch **4608×2592** — Konstante `RPI_CAMERA_MODULE3_IMX708_MAX_SIZE` in `services/camera.py`; nach `open()` liefert `configured_main_size` die tatsächlich konfigurierte Größe |
| `use_still_configuration` | `True` | `True`: Picamera2 **Still**-Pfad (bessere Bildqualität als reine Vorschau); `False`: **Preview**-Pfad (oft höhere FPS) |
| `square_crop` | `False` | Quadratischen Mittelschnitt aktivieren |
| `lens_position` | `5.0` | Manuelle Fokus-Position in Dioptrien (`1/m`); Standard für **20 cm** Abstand zur Arbeitsfläche |
| `picamera_rgb_buffer` | `True` | Nach `capture_array()` von RGB→BGR wandeln (Picamera2 liefert oft RGB-Reihenfolge; sonst wirken Hauttöne bläulich) |
| `lock_focus` | `True` | Autofokus fixieren (nur Picamera2) |

### Verwendung

Immer als Context Manager — die Kamera wird automatisch freigegeben, auch bei Fehlern:

```python
# Standard
with CameraService() as cam:
    ret, frame = cam.read()  # gleiche Signatur wie cv2.VideoCapture.read()

# Quadratischer Crop (z.B. 1080×1080)
with CameraService(output_size=(1920, 1080), square_crop=True) as cam:
    ret, frame = cam.read()  # → (1080, 1080, 3)
```

### Installation auf dem Raspberry Pi

`picamera2` ist **nicht** in `pyproject.toml` eingetragen (Linux-only, würde auf macOS beim Build fehlschlagen). Separat installieren:

```bash
sudo apt install python3-picamera2
```

---

## `calibrate/__main__.py` — CLI

```bash
uv run python -m calibrate <command>
```

| Command | Beschreibung |
|---|---|
| `generate-markers` | Generiert ArUco Marker PNGs nach `data/calibration/markers/` |
| `detect` | Live ArUco-Erkennung vom Kamerabild |
| `take-photos` | Nimmt alle 2 s ein Foto auf, speichert nach `data/calibration/photos/` |
| `calibrate` | Kalibriert die Kamera aus den gespeicherten Fotos |

---

## Kalibrierungsworkflow

### Konfiguration (`camera_calibration.py`)

| Konstante | Wert | Bedeutung |
|---|---|---|
| `SQUARE_SIZE` | `0.23` m | Seitenlänge eines Schachbrettfeldes |
| `GRID` | `(9, 6)` | Innere Eckpunkte (nicht Felder) |
| `PHOTOS_DIR` | `data/calibration/photos/` | Eingabeverzeichnis |
| `OUTPUT_DIR` | `data/calibration/undistorted/` | Undistorted Bilder |
| `CALIBRATION_FILE` | `camera.yml` | Ausgabe im Projektwurzelverzeichnis |

> `GRID` sind die **inneren** Schnittpunkte des Gitters. Ein Schachbrett mit 10×7 Feldern hat `(9, 6)` innere Eckpunkte.

### Schritt 1 — Fotos aufnehmen

```bash
uv run python -m calibrate take-photos
# optional feste Auflösung statt voller Sensor:
# uv run python -m calibrate take-photos --size 1920x1080
```

- Löscht alle vorhandenen Fotos im Ordner `data/calibration/photos/` beim Start
- Standard: **volle Sensorauflösung** (Picamera2) für schärfere Kalibrierfotos; mit `--size WxH` z. B. 1080p
- Zeigt Live-Vorschau, speichert automatisch alle **3 Sekunden** ein Foto
- Stoppt automatisch nach **25 Fotos** (Standard)
- Manueller Abbruch jederzeit mit `q`
- Schachbrett bewusst auch in die **Bildecken und -ränder** halten — dort ist die Weitwinkelverzerrung am stärksten

> Die Fotos werden nicht ins Git eingecheckt (`.gitignore`).

### Schritt 2 — Kalibrierung ausführen

```bash
uv run python -m calibrate calibrate
```

Ablauf:

1. Lädt alle PNGs aus `data/calibration/photos/`
2. Sucht das Schachbrett-Gitter in jedem Bild (`findChessboardCorners`)
3. Bilder ohne Erkennung werden automatisch übersprungen
4. Berechnet Kameraparameter mit **Rational Model** (`cv2.CALIB_RATIONAL_MODEL`) — 8 Distortion-Koeffizienten statt 5, besser geeignet für das 102° Weitwinkelobjektiv des Pi Camera Module 3 Wide/NoIR
5. Speichert undistorted Bilder nach `data/calibration/undistorted/`
6. Schreibt `camera.yml` mit `matrix`, `new_matrix`, `distortion_coef` und `calibration_size`
7. Gibt den Re-Projection Error aus

### Live-Erkennung (`detect`)

`uv run python -m calibrate detect` lädt `camera.yml` (falls vorhanden) und **entzerrt** jedes Bild vor der ArUco-Erkennung (`undistort`), damit die Kalibrierung wirksam wird.

```bash
uv run python -m calibrate detect --no-calibration    # ohne Entzerrung testen
uv run python -m calibrate detect --calibration /pfad/zur/camera.yml
```

**Hinweis:** Ältere `camera.yml` ohne Eintrag `matrix` müssen einmal neu mit `calibrate` erzeugt werden.

### Re-Projection Error

| Wert | Bewertung |
|---|---|
| `< 0.5` | Gut |
| `0.5 – 1.0` | Akzeptabel |
| `> 1.0` | Fotos wiederholen, Fokus prüfen |

---

## `camera.yml` — Kalibrierungsresultat

Gespeichert im OpenCV YAML-Format. Enthält:

- `matrix` — originale Kameramatrix aus `calibrateCamera` (3×3), nötig für `undistort`
- `new_matrix` — optimierte Matrix nach `getOptimalNewCameraMatrix`
- `distortion_coef` — Distortion-Koeffizienten (1×8, Rational Model)
- `calibration_size` — Bildgröße `(Breite, Höhe)` der Kalibrierfotos (für Skalierung bei anderer Live-Auflösung)

### Laden für Pose-Estimation

```python
cv_file = cv2.FileStorage("camera.yml", cv2.FILE_STORAGE_READ)
mtx = cv_file.getNode("matrix").mat()
new_matrix = cv_file.getNode("new_matrix").mat()
dist_coef  = cv_file.getNode("distortion_coef").mat()
cv_file.release()
```

---

## Offene TODOs

- [x] `LensPosition` Standard **5.0** (= 20 cm Abstand zur Arbeitsfläche); Kalibrierbereich: A4 + Reserve (keine volle Tischfläche nötig)
