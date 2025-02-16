import pickle
import cv2
import mediapipe as mp
import numpy as np
import random
import random
import time

model_dict = pickle.load(open('./model.p', 'rb'))
model = model_dict['model']

cap = cv2.VideoCapture(0)

# กำหนด Mediapipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.8)

# คำที่ต้องพิมพ์
words = ["BALL", "LBAB", "A", "B", "L", "LL"]
current_word = random.choice(words)  # สุ่มคำ
typed_word = ""  # ตัวอักษรที่พิมพ์ไปแล้ว

last_character = None
frame_counter = 0
typing_delay = 15

labels_dict = {0: 'A', 1: 'B', 2: 'L'}

if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    data_aux = []
    x_ = []
    y_ = []

    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break       

    H, W, _ = frame.shape

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # ประมวลผล Mediapipe
    results = hands.process(frame_rgb)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )

            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                data_aux.append(x)
                data_aux.append(y)
                x_.append(x)
                y_.append(y)

        x1 = int(min(x_) * W) - 10
        y1 = int(min(y_) * H) - 10
        x2 = int(max(x_) * W) + 10
        y2 = int(max(y_) * H) + 10

        # คำนวณความหลี่เป๊ะ
        predicted_character = ""
        confidence_score = 0.0
        prediction = model.predict([np.asarray(data_aux)]) # class ที่ทำนาย
        prob = model.predict_proba([np.asarray(data_aux)]) # prob ของแต่ละ class
        prediction = np.argmax(prob) 
        confidence_score = np.max(prob) 

        # predicted_character = labels_dict[int(prediction[0])]
        # print(predicted_character)

        # แปลงโดยดึงค่ามาจาก labels_dict
        predicted_character = labels_dict.get(prediction, "")
        print(predicted_character)

        # ตรวจสอบว่าตัวอักษรเป็นตัวถัดไปในคำที่กำลังพิมพ์
        if predicted_character and confidence_score > 0.7:
            if predicted_character == current_word[len(typed_word)]:
                # ป้องกกันการตรวจจับซ้ำ
                if predicted_character != last_character:
                    frame_counter = 0
                    last_character = predicted_character
                else:
                    frame_counter += 1

                if frame_counter >= typing_delay:
                    typed_word += predicted_character  # เพิ่มตัวอักษรที่พิมพ์ไปแล้ว
                    frame_counter = 0


        # ถ้าพิมพ์ครบทั้งคำแล้ว ให้สุ่มคำใหม่
        if typed_word == current_word:
            time.sleep(1)
            current_word = random.choice(words)
            typed_word = ""


        # แสดงคำที่ต้องพิมพ์
        cv2.putText(frame, f"Word: {current_word}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3, cv2.LINE_AA)

        # แสดงคำที่พิมพ์ได้
        cv2.putText(frame, f"Your Input: {typed_word}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3, cv2.LINE_AA)

        # วาดกรอบ check ความหลี่เป๊ะ
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
        cv2.putText(frame, f'{predicted_character} ({confidence_score*100:.2f}%)', 
                    (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3, cv2.LINE_AA)


    cv2.imshow('Alpha Signing Test', frame)
    if cv2.waitKey(1) & 0xFF == ord('e'):
        break

cap.release()
cv2.destroyAllWindows()
