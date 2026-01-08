import cv2
import numpy as np
import os

recognizer = cv2.face.LBPHFaceRecognizer_create()
FACE_DATASET = "dataset"

os.makedirs(FACE_DATASET, exist_ok=True)

def capture_face(user_id):
    cap = cv2.VideoCapture(0)
    count = 0
    user_path = f"{FACE_DATASET}/{user_id}"
    os.makedirs(user_path, exist_ok=True)

    while count < 20:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f"{user_path}/{count}.jpg", gray)
        count += 1

    cap.release()
    train_model()   # 🔥 VERY IMPORTANT


def train_model():
    faces, labels = [], []

    for user_id in os.listdir(FACE_DATASET):
        for img in os.listdir(f"{FACE_DATASET}/{user_id}"):
            path = f"{FACE_DATASET}/{user_id}/{img}"
            faces.append(cv2.imread(path, 0))
            labels.append(int(user_id))

    recognizer.train(faces, np.array(labels))
    recognizer.save("face_model.yml")

def recognize_face():
    if not os.path.exists("face_model.yml"):
        return None, None  # model not trained yet

    recognizer.read("face_model.yml")

    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return None, None

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    label, confidence = recognizer.predict(gray)

    return label, confidence