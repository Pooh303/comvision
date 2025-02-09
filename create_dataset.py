import os
import mediapipe as mp
import cv2
import pickle
import matplotlib as plt


# กำหนด Mediapipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.8)

DATA_DIR = './data'

data = []
labels = []

# ตรวจสอบโฟลเดอร์
if not os.path.exists(DATA_DIR):
    print(f"Directory {DATA_DIR} does not exist.")
    exit()

if not os.listdir(DATA_DIR):
    print(f"Directory {DATA_DIR} is empty.")
    exit()

# ประมวลผลไฟล์
for dirpath, dirnames, filenames in os.walk(DATA_DIR):
    for filename in filenames:
        file_path = os.path.join(dirpath, filename)
        data_aux = []

        if filename.endswith('.jpg'):  # ตรวจสอบเฉพาะไฟล์ .png

            # อ่านและแปลงภาพ
            img = cv2.imread(file_path)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # ประมวลผล Mediapipe
            results = hands.process(img_rgb)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    for i in range(len(hand_landmarks.landmark)):
                        x = hand_landmarks.landmark[i].x
                        y = hand_landmarks.landmark[i].y
                        data_aux.append(x)
                        data_aux.append(y)


                    print(f"Data for {filename}")
                    data.append(data_aux)
                    labels.append(os.path.basename(dirpath))
            else:
                print(f"No hands detected in: {file_path}")

f = open('data.pickle', 'wb')
pickle.dump({'data': data, 'labels': labels}, f)
f.close()