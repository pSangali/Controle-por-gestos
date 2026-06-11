"""
Controle de slides por gestos — versão Wayland (python-uinput)

  Mindinho levantado  ->  proximo slide   (seta direita)
  Polegar levantado   ->  slide anterior  (seta esquerda)
  ESC                 ->  sair

Setup:
    pip install mediapipe opencv-python numpy python-uinput
    sudo modprobe uinput

    Rode com: sudo python hands_presentation.py

    Baixe o modelo (uma vez) e deixe na mesma pasta deste script:
    https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
"""

import os
import time

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
import uinput

# ------------------------- configuracao -------------------------
MODEL_PATH = "hand_landmarker.task"
CAM_INDEX = 0
COOLDOWN = 1.0
ARROW_SHOW_TIME = 0.6
ARROW_SIZE = (246, 166)

# ------------------------- preparacao ---------------------------
if not os.path.exists(MODEL_PATH):
    raise SystemExit(
        f"Modelo '{MODEL_PATH}' nao encontrado.\n"
        "Baixe em: https://storage.googleapis.com/mediapipe-models/"
        "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    )

device = uinput.Device([uinput.KEY_RIGHT, uinput.KEY_LEFT])
time.sleep(1)  # espera o device inicializar


def load_arrow(path):
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"[aviso] '{path}' nao encontrada — a seta nao sera exibida.")
        return None
    return cv2.resize(img, ARROW_SIZE)


seta_dir = load_arrow("seta dir.PNG")
seta_esq = load_arrow("seta esq.PNG")


def overlay(frame, arrow, x, y):
    if arrow is None:
        return
    h, w = arrow.shape[:2]
    H, W = frame.shape[:2]
    if x < 0 or y < 0 or x + w > W or y + h > H:
        return
    roi = frame[y:y + h, x:x + w]
    if arrow.shape[2] == 4:
        alpha = arrow[:, :, 3:4] / 255.0
        rgb = arrow[:, :, :3]
        frame[y:y + h, x:x + w] = (alpha * rgb + (1 - alpha) * roi).astype(np.uint8)
    else:
        frame[y:y + h, x:x + w] = arrow


def fingers_up(lm, handed):
    f = []
    if handed == "Right":
        f.append(1 if lm[4].x < lm[3].x else 0)
    else:
        f.append(1 if lm[4].x > lm[3].x else 0)
    for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        f.append(1 if lm[tip].y < lm[pip].y else 0)
    return f


def press_key(direction):
    if direction == "right":
        device.emit_click(uinput.KEY_RIGHT)
    else:
        device.emit_click(uinput.KEY_LEFT)


# ------------------------- detector -----------------------------
options = vision.HandLandmarkerOptions(
    base_options=mp_python.BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.6,
)
landmarker = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(CAM_INDEX)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

ultimo_gesto = 0.0
seta_ativa = None

# ------------------------- loop ---------------------------------
while True:
    ok, frame = cap.read()
    if not ok:
        break
    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    ts = int(time.time() * 1000)
    result = landmarker.detect_for_video(mp_image, ts)

    agora = time.time()
    if result.hand_landmarks:
        lm = result.hand_landmarks[0]
        handed = result.handedness[0][0].category_name
        estado = fingers_up(lm, handed)

        if agora - ultimo_gesto > COOLDOWN:
            if estado == [0, 0, 0, 0, 1]:        # mindinho
                press_key("right")
                ultimo_gesto = agora
                seta_ativa = ("dir", agora + ARROW_SHOW_TIME)
                print("proximo slide")
            elif estado == [1, 0, 0, 0, 0]:      # polegar
                press_key("left")
                ultimo_gesto = agora
                seta_ativa = ("esq", agora + ARROW_SHOW_TIME)
                print("slide anterior")

    if seta_ativa and agora < seta_ativa[1]:
        if seta_ativa[0] == "dir":
            overlay(frame, seta_dir, frame.shape[1] - ARROW_SIZE[0] - 30, 50)
        else:
            overlay(frame, seta_esq, 30, 50)
    else:
        seta_ativa = None

    cv2.imshow("Controle de slides", cv2.resize(frame, (960, 540)))
    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()