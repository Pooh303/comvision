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
    def __init__(self, model_path='./model.p', words_file='words.txt', max_word_length=4, use_brown=False):
        """
        คอนสตรัคเตอร์ของคลาส
        โหลดโมเดล และเตรียมตัวแปรที่ใช้ในเกม เช่น คำศัพท์ ตัวจับเวลา และคะแนน
        """
        model_dict = pickle.load(open(model_path, 'rb'))
        self.model = model_dict['model']
        self.labels_dict = {i: letter for i, letter in enumerate(string.ascii_uppercase)}
        self.words_file = words_file
        self.words = self.load_words(max_word_length, use_brown)  # โหลดหรือสร้างคำศัพท์

        self.current_word = random.choice(self.words)
        self.typed_word = ""
        self.start_time = time.time()
        self.elapsed_time = 0
        self.time_limit = 3
        self.score = 0
        self.last_character = None
        self.frame_counter = 0
        self.typing_delay = 15

        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.hands = self.mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.5)

    def generate_lba_words(self, max_length, use_brown_corpus=False):
        """
        สร้างคำศัพท์ที่เป็นไปได้จากตัวอักษร A-Z และตรวจสอบว่ามีอยู่จริงในฐานข้อมูล NLTK หรือไม่
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
        สร้างไฟล์คำศัพท์โดยใช้คำที่ผ่านการตรวจสอบว่ามีอยู่จริง
        """
        words = self.generate_lba_words(max_length, use_brown)
        with open(self.words_file, "w") as f:
            f.writelines(f"{word}\n" for word in words)

        print(f"{self.words_file} ถูกสร้างขึ้นแล้ว มีคำทั้งหมด {len(words)} คำ")

    def load_words(self, max_length, use_brown):
        """
        โหลดคำศัพท์จากไฟล์ หากไม่มีไฟล์ จะทำการสร้างขึ้นมาใหม่
        """
        if not os.path.exists(self.words_file):
            print(f"ไม่พบไฟล์ '{self.words_file}' กำลังสร้างไฟล์คำศัพท์...")
            self.create_words_file(max_length, use_brown)

        try:
            with open(self.words_file, 'r') as f:
                words = [line.strip().upper() for line in f if line.strip()]
                if not words:
                    raise ValueError("ไม่พบคำศัพท์ในไฟล์")
                return words
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการโหลดคำ: {e}")
            return ["APPLE", "BALL", "CAT", "DOG", "EASY",  
        "FISH", "GOAT", "HOUSE", "IRON", "JUMP",  
        "KITE", "LION", "MONKEY", "NEST", "ORANGE",  
        "PENCIL", "QUEEN", "RABBIT", "SUN", "TIGER",  
        "UMBRELLA", "VIOLIN", "WATER", "XYLOPHONE", "YELLOW", "ZEBRA"]


    def predict(self, frame):
        """
        คาดการณ์ตัวอักษรจากภาพมือโดยใช้โมเดล AI
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            data_aux = [coord for landmark in hand_landmarks.landmark for coord in (landmark.x, landmark.y)]

            prediction = self.model.predict([np.asarray(data_aux)])
            prob = self.model.predict_proba([np.asarray(data_aux)])
            predicted_character = self.labels_dict.get(np.argmax(prob), "")
            confidence_score = np.max(prob)

            return predicted_character, confidence_score, results, hand_landmarks
        return None, None, None, None

    def process_prediction(self, predicted_character, confidence_score):
        """
        ตรวจสอบว่าตัวอักษรที่คาดการณ์ได้ถูกต้องหรือไม่ และเพิ่มไปยังคำที่กำลังพิมพ์
        """
        if predicted_character and confidence_score > 0.5:
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
        ตรวจสอบว่าผู้ใช้พิมพ์คำศัพท์ครบถ้วนหรือไม่ หากครบให้เริ่มคำใหม่
        """
        if self.typed_word == self.current_word:
            self.elapsed_time = time.time() - self.start_time
            if self.elapsed_time <= self.time_limit:
                self.score += 1
            self.reset_word()
            return True, self.elapsed_time
        return False, 0

    def update_timer(self):
        """
        อัปเดตเวลาที่เหลือสำหรับการพิมพ์คำศัพท์
        """
        remaining_time = self.time_limit - (time.time() - self.start_time)
        if remaining_time <= 0:
            if self.typed_word == self.current_word:
                self.score += 1
            self.reset_word()
            return 0
        return max(0, remaining_time)

    def reset_word(self):
        """
        รีเซ็ตค่าและเลือกคำศัพท์ใหม่เมื่อหมดเวลา หรือเมื่อพิมพ์ถูกต้อง
        """
        time.sleep(1)
        self.current_word = random.choice(self.words)
        self.typed_word = ""
        self.start_time = time.time()
        self.elapsed_time = 0

    def get_game_state(self):
        """
        คืนค่าข้อมูลสถานะของเกม เช่น คำศัพท์ปัจจุบัน คำที่พิมพ์ คะแนน และเวลาที่เหลือ
        """
        return {
            "current_word": self.current_word,
            "typed_word": self.typed_word,
            "score": self.score,
            "remaining_time": self.update_timer()
        }
