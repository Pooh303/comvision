import pickle
import cv2
import mediapipe as mp
import numpy as np
import random
import time
import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage


model_dict = pickle.load(open('./model.p', 'rb'))
model = model_dict['model']

# กำหนด Mediapipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.8)

# Map Labels
labels_dict = {0: 'A', 1: 'B', 2: 'L'}

# คำที่ต้องพิมพ์
words = ["BALL", "LBAB", "A", "B", "L", "LL"]
current_word = random.choice(words)  # สุ่มคำ
typed_word = ""  # ตัวอักษรที่พิมพ์ไปแล้ว

# จับเวลาการพิมพ์
start_time = time.time()
elapsed_time = 0
time_limit = 3  # ตั้งเวลานับถอยหลัง 3 วินาที
score = 0  # คะแนนเริ่มต้น

last_character = None
frame_counter = 0
typing_delay = 15

# สร้าง GUI
root = ctk.CTk()
root.geometry("1000x700")
root.title("Sign Language Recognition")

lbl_video = ctk.CTkLabel(root)
lbl_video.pack()

lbl_result = ctk.CTkLabel(root, text="Prediction: ", font=("Arial", 24))
lbl_result.pack(pady=10)

lbl_word = ctk.CTkLabel(root, text=f"Word: {current_word}", font=("Arial", 20))
lbl_word.pack()

lbl_typed = ctk.CTkLabel(root, text=f"Your Input: {typed_word}", font=("Arial", 20))
lbl_typed.pack()

lbl_time = ctk.CTkLabel(root, text=f"Time: {elapsed_time:.2f} sec", font=("Arial", 18))
lbl_time.pack()

lbl_score = ctk.CTkLabel(root, text=f"Score: {score}", font=("Arial", 18))
lbl_score.pack()

btn_exit = ctk.CTkButton(root, text="Exit", command=root.quit)
btn_exit.pack(pady=10)

# เปิดกล้อง
cap = cv2.VideoCapture(0)

def update_frame():
    global typed_word, last_character, frame_counter, current_word, start_time, elapsed_time, time_limit, score

    ret, frame = cap.read()
    if not ret:
        return

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame)
    img_ctk = CTkImage(light_image=img, dark_image=img, size=(640, 480))  # ✅ กำหนดขนาดให้เหมาะสม

    lbl_video.configure(image=img_ctk)
    lbl_video.imgtk = img_ctk  # ป้องกัน GC ลบรูป
    
    # ✅ ประมวลผล Mediapipe
    results = hands.process(frame)
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        data_aux = []
        x_ = []
        y_ = []

        for i in range(len(hand_landmarks.landmark)):
            x = hand_landmarks.landmark[i].x
            y = hand_landmarks.landmark[i].y
            data_aux.append(x)
            data_aux.append(y)
            x_.append(x)
            y_.append(y)
    
        prediction = model.predict([np.asarray(data_aux)])
        prob = model.predict_proba([np.asarray(data_aux)])
        predicted_character = labels_dict.get(np.argmax(prob), "")
        confidence_score = np.max(prob)

        lbl_result.configure(text=f"Prediction: {predicted_character} ({confidence_score * 100:.2f}%)")

        # ตรวจสอบว่าตัวอักษรถูกต้อง
        if predicted_character and confidence_score > 0.5:
            if len(typed_word) < len(current_word) and predicted_character == current_word[len(typed_word)]:
                if predicted_character != last_character:
                    frame_counter = 0
                    last_character = predicted_character
                else:
                    frame_counter += 1

                if frame_counter >= typing_delay:
                    typed_word += predicted_character
                    frame_counter = 0
                    lbl_typed.configure(text=f"Your Input: {typed_word}")

        # ถ้าพิมพ์ครบแล้วให้สุ่มคำใหม่
        if typed_word == current_word:
            end_time = time.time()
            elapsed_time = end_time - start_time
            lbl_time.configure(text=f"Time: {elapsed_time:.2f} sec")

            if elapsed_time <= time_limit:
                score += 1
                lbl_score.configure(text=f"Score: {score}")

            time.sleep(1)
            current_word = random.choice(words)
            typed_word = ""
            start_time = time.time()
            lbl_word.configure(text=f"Word: {current_word}")
            lbl_typed.configure(text="Your Input: ")

    # คำนวณเวลานับถอยหลัง
    remaining_time = time_limit - (time.time() - start_time)
    lbl_time.configure(text=f"Time: {max(0, remaining_time):.2f} sec")

    if remaining_time <= 0:
        # หมดเวลา, ตรวจสอบคำที่พิมพ์
        if typed_word == current_word:
            score += 1
            lbl_score.configure(text=f"Score: {score}")
        current_word = random.choice(words)
        typed_word = ""
        start_time = time.time()
        lbl_word.configure(text=f"Word: {current_word}")
        lbl_typed.configure(text="Your Input: ")

    lbl_video.after(10, update_frame)

update_frame()
root.mainloop()

cap.release()
cv2.destroyAllWindows()
