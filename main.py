import cv2
import time
import os
import urllib.request
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui

# Optional: PyAutoGUI Sicherheitsnetz (stoppt nicht, wenn die Maus in die Ecke schnellt)
pyautogui.FAILSAFE = False

# Modell automatisch herunterladen, falls nicht vorhanden
model_path = 'face_landmarker.task'
if not os.path.exists(model_path):
    print("Lade das MediaPipe Face Landmarker Modell herunter (ca. 45 MB)...")
    url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
    urllib.request.urlretrieve(url, model_path)
    print("Download abgeschlossen!")

# MediaPipe Face Landmarker initialisieren (im VIDEO-Modus)
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_faces=1,
    output_face_blendshapes=True
)
detector = vision.FaceLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

start_time = time.time()
previous_eyes_closed = False
previous_brows_furrowed = False
last_scroll_time = 0.0
scroll_cooldown = 0.1
scroll_amount = -15
blink_threshold = 0.3
brow_threshold = 0.45
last_like_time = 0.0
like_cooldown = 1.0
should_exit = False


def landmark_distance(first, second):
    return ((first.x - second.x) ** 2 + (first.y - second.y) ** 2) ** 0.5

print("Bereit: Blinzeln scrollt, Mund öffnen beendet das Skript.")

with detector:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        # Bild spiegeln und in RGB umwandeln
        image = cv2.flip(image, 1)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # In MediaPipe Image Format konvertieren
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
        
        # Fortlaufenden Zeitstempel in Millisekunden berechnen
        timestamp_ms = int((time.time() - start_time) * 1000)
        
        # Gesichtserkennung für Video-Streams ausführen
        results = detector.detect_for_video(mp_image, timestamp_ms)

        if results.face_landmarks:
            for face_landmarks in results.face_landmarks:
                mouth_open_ratio = landmark_distance(face_landmarks[13], face_landmarks[14]) / landmark_distance(
                    face_landmarks[78], face_landmarks[308]
                )
                if mouth_open_ratio > 0.38:
                    cv2.putText(image, "MUND OFFEN - BEENDEN", (30, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    should_exit = True
                    break

                blendshape_scores = {
                    category.category_name: category.score
                    for category in results.face_blendshapes[0]
                }
                brows_furrowed = (
                    blendshape_scores.get("browDownLeft", 0.0)
                    + blendshape_scores.get("browDownRight", 0.0)
                ) / 2 > brow_threshold
                if brows_furrowed and not previous_brows_furrowed and time.time() - last_like_time >= like_cooldown:
                    screen_width, screen_height = pyautogui.size()
                    pyautogui.doubleClick(screen_width // 2, screen_height // 2, interval=0.08)
                    last_like_time = time.time()
                    cv2.putText(image, "LIKE", (30, 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
                previous_brows_furrowed = brows_furrowed

                blink_score = (
                    blendshape_scores.get("eyeBlinkLeft", 0.0)
                    + blendshape_scores.get("eyeBlinkRight", 0.0)
                ) / 2
                eyes_closed = blink_score > blink_threshold

                # Nur beim Übergang zu geschlossenen Augen scrollen, nicht in jedem Frame.
                if eyes_closed and not previous_eyes_closed and time.time() - last_scroll_time >= scroll_cooldown:
                    pyautogui.scroll(scroll_amount)
                    last_scroll_time = time.time()
                    cv2.putText(image, "BLINK - SCROLL DOWN", (30, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                elif eyes_closed:
                    cv2.putText(image, "AUGEN GESCHLOSSEN", (30, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                else:
                    cv2.putText(image, "BLINKEN ZUM SCROLLEN", (30, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                previous_eyes_closed = eyes_closed

        if should_exit:
            break

        cv2.imshow('Head Tracking Scroll', image)

        # Mit der Taste 'q' beenden
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()