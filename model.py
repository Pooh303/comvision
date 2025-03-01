import pickle
import mediapipe as mp
import numpy as np
import random
import time
import cv2
import string
import itertools
import nltk
from nltk.corpus import words as nltk_words
from nltk.corpus import brown
import os
import playsound

# ตรวจสอบว่ามีไฟล์คำศัพท์ของ NLTK หรือไม่ ถ้าไม่มีให้ดาวน์โหลด
try:
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('words')

try:
    nltk.data.find('corpora/brown')
except LookupError:
    nltk.download('brown')

class SignLanguageModel:
    def __init__(self, model_path='./model_best.p', words_file='words.txt', max_word_length=4, use_brown=False):
        """
        เริ่มต้นคลาส SignLanguageModel
        โหลดโมเดล, ตั้งค่า MediaPipe, และเตรียมตัวแปรสำหรับเกม

        Args:
            model_path (str): พาธไปยังไฟล์โมเดลที่บันทึกไว้ (.p).  ค่าเริ่มต้นคือ './model_best.p'
            words_file (str): พาธไปยังไฟล์ข้อความที่เก็บคำศัพท์. ค่าเริ่มต้นคือ 'words.txt'
            max_word_length (int): ความยาวสูงสุดของคำศัพท์ที่จะใช้ในเกม. ค่าเริ่มต้นคือ 4
            use_brown (bool):  ใช้ Brown Corpus สำหรับคำศัพท์หรือไม่ (True/False). ค่าเริ่มต้นคือ False.
        """
        model_dict = pickle.load(open(model_path, 'rb'))
        self.model = model_dict['model']

        letters = string.ascii_uppercase.replace('J', '').replace('Z', '')
        self.labels_dict = {i: letter for i, letter in enumerate(letters)}

        self.words_file = words_file
        self.words = self.load_words(max_word_length, use_brown)

        self.current_word = random.choice(self.words)
        self.typed_word = ""
        self.start_time = time.time()
        self.elapsed_time = 0
        self.time_limit = 10
        self.score = 0
        self.last_character = None
        self.frame_counter = 0
        self.typing_delay = 15

        # ตั้งค่า MediaPipe (แบบง่าย)
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.hands = self.mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.3)  # ปรับ confidence


    def generate_lba_words(self, max_length, use_brown_corpus=False):
        """
        สร้างคำศัพท์ที่เป็นไปได้จากตัวอักษร A-Z และตรวจสอบกับ NLTK.

        Args:
            max_length (int): ความยาวสูงสุดของคำ
            use_brown_corpus (bool): ใช้ Brown Corpus หรือไม่

        Returns:
            list: รายการคำศัพท์ที่ถูกต้อง
        """
        letters = string.ascii_uppercase
        english_words = set(word.lower() for word in (brown.words() if use_brown_corpus else nltk_words.words()))

        real_words = sorted(
            word for length in range(1, max_length + 1)
            for comb in itertools.product(letters, repeat=length)
            if (word := "".join(comb).lower()) in english_words
        )

        return real_words

    def create_words_file(self, max_length, use_brown=False):
        """
        สร้างไฟล์คำศัพท์ที่ถูกต้อง.

        Args:
            max_length (int): ความยาวสูงสุดของคำ
            use_brown (bool): ใช้ Brown Corpus หรือไม่
        """
        words = self.generate_lba_words(max_length, use_brown)
        with open(self.words_file, "w") as f:
            f.writelines(f"{word}\n" for word in words)

        print(f"{self.words_file} ถูกสร้างขึ้นด้วยจำนวน {len(words)} คำ.")

    def load_words(self, max_length, use_brown):
        """
        โหลดคำศัพท์จากไฟล์หรือสร้างไฟล์ใหม่.

        Args:
            max_length (int): ความยาวสูงสุดของคำ.
            use_brown (bool): ใช้ Brown Corpus หรือไม่.

        Returns:
            list: รายการคำศัพท์.
        """
        if not os.path.exists(self.words_file):
            print(f"ไม่พบ '{self.words_file}'. กำลังสร้าง...")
            self.create_words_file(max_length, use_brown)

        try:
            with open(self.words_file, 'r') as f:
                words = [line.strip().upper() for line in f if line.strip()]
                if not words:
                    raise ValueError("ไม่พบคำศัพท์ในไฟล์.")
                return words
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการโหลดคำ: {e}")
            return ["APPLE", "BALL", "CAT", "DOG", "EASY", "FISH", "GOAT", "HOUSE"]  # รายการคำเริ่มต้น (สั้นลง)

    def predict(self, frame):
        """
        ทำนายอักษรภาษามือจากเฟรม.

        Args:
            frame (np.ndarray): เฟรมภาพจาก OpenCV.

        Returns:
            tuple: (predicted_character, predicted_proba, results, hand_landmarks)
                - predicted_character (str): อักษรที่ทำนายได้ (หรือ None ถ้าไม่พบมือ).
                - predicted_proba (float): ความน่าจะเป็นของอักษรที่ทำนายได้ (หรือ None).
                - results: ผลลัพธ์ดิบจาก MediaPipe.
                - hand_landmarks: ตำแหน่ง landmarks ของมือ (หรือ None).
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]  # มือแรก
            data_aux = []
            x_ = []
            y_ = []

            for landmark in hand_landmarks.landmark:
                x = landmark.x
                y = landmark.y
                x_.append(x)
                y_.append(y)

            for landmark in hand_landmarks.landmark:
                x = landmark.x
                y = landmark.y
                # Normalize โดยการลบค่า min (ตามตัวอย่างโค้ดที่สอง)
                data_aux.append(x - min(x_))
                data_aux.append(y - min(y_))

            prediction = self.model.predict([np.asarray(data_aux)])
            prediction_proba = self.model.predict_proba([np.asarray(data_aux)])
            predicted_character = self.labels_dict.get(int(prediction[0]), "")
            predicted_proba = np.max(prediction_proba)

            return predicted_character, predicted_proba, results, hand_landmarks  # คืนค่า results และ landmarks
        return None, None, None, None  # สำคัญ: คืนค่า None ถ้าไม่พบมือ

    def process_prediction(self, predicted_character, confidence_score):
        """
        ตรวจสอบว่าอักษรที่ทำนายถูกต้องหรือไม่ และเพิ่มลงในคำที่พิมพ์.

        Args:
            predicted_character (str): อักษรที่ทำนายได้.
            confidence_score (float): ค่าความเชื่อมั่น.

        Returns:
            bool: True ถ้าอักษรถูกต้องและถูกเพิ่ม, False ถ้าไม่.
        """
        if predicted_character and confidence_score > 0.5:  # เกณฑ์ความเชื่อมั่น
            if len(self.typed_word) < len(self.current_word) and predicted_character == self.current_word[len(self.typed_word)]:
                if predicted_character != self.last_character:
                    self.frame_counter = 0
                    self.last_character = predicted_character
                else:
                    self.frame_counter += 1

                if self.frame_counter >= self.typing_delay:
                    self.typed_word += predicted_character
                    self.frame_counter = 0
                    return True
        return False

    def check_word_completion(self):
        """
        ตรวจสอบว่าผู้ใช้พิมพ์คำศัพท์เสร็จหรือไม่.

        Returns:
            tuple: (bool, float)
                - bool:  True ถ้าพิมพ์คำเสร็จ, False ถ้าไม่.
                - float: เวลาที่ใช้ในการพิมพ์คำ (ถ้าเสร็จ).
        """
        if self.typed_word == self.current_word:
            self.elapsed_time = time.time() - self.start_time
            if self.elapsed_time <= self.time_limit:
                self.score += 1
            self.reset_word()
            playsound.playsound("assets/sound/CorrectSound.mp3", block=False)  # เล่นเสียง
            return True, self.elapsed_time
        return False, 0

    def update_timer(self):
        """
        อัปเดตเวลาที่เหลือสำหรับการพิมพ์.

        Returns:
            float: เวลาที่เหลือ (วินาที).
        """
        remaining_time = self.time_limit - (time.time() - self.start_time)
        if remaining_time <= 0:
            if self.typed_word == self.current_word:  # ตรวจสอบว่าพิมพ์เสร็จหรือไม่เมื่อหมดเวลา
                self.score += 1
            self.reset_word()
            return 0
        return max(0, remaining_time)

    def reset_word(self):
        """
        รีเซ็ตคำศัพท์และตัวจับเวลา.
        """
        time.sleep(1)  # หยุดชั่วคราว
        self.current_word = random.choice(self.words)
        self.typed_word = ""
        self.start_time = time.time()
        self.elapsed_time = 0

    def get_game_state(self):
        """
        คืนค่าสถานะปัจจุบันของเกม.

        Returns:
            dict:  พจนานุกรมที่มีสถานะของเกม:
                - "current_word": คำศัพท์ปัจจุบัน.
                - "typed_word": คำที่พิมพ์ไปแล้ว.
                - "score": คะแนน.
                - "remaining_time": เวลาที่เหลือ.
        """
        return {
            "current_word": self.current_word,
            "typed_word": self.typed_word,
            "score": self.score,
            "remaining_time": self.update_timer()
        }