# model.py (Modified)
import pickle
import mediapipe as mp
import numpy as np
import random
import time
import cv2


class SignLanguageModel:
    def __init__(self, model_path='./model.p', words_file='words.txt'):
        model_dict = pickle.load(open(model_path, 'rb'))
        self.model = model_dict['model']
        self.labels_dict = {0: 'A', 1: 'B', 2: 'L'}
        self.words = self.load_words(words_file)  # Load words from file
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
        # Use tracking (static_image_mode=False) and adjust confidence
        self.hands = self.mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.5)

    def load_words(self, words_file):
        """Loads words from a text file, one word per line."""
        try:
            with open(words_file, 'r') as f:
                words = [line.strip().upper() for line in f]  # Read, strip whitespace, and convert to uppercase
                # Filter our empty lines
                words = [word for word in words if word] # Keep only non-empty words
                if not words:
                    raise ValueError("No words found in the file.") #prevent crash
                return words
        except FileNotFoundError:
            print(f"Error: Words file '{words_file}' not found.  Using default words.")
            return ["BALL", "LBAB", "A", "B", "L", "LL"]  # Default words
        except Exception as e:
            print(f"Error loading words from file: {e}. Using default words")
            return ["BALL", "LBAB", "A", "B", "L", "LL"]

    def predict(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            data_aux = []
            for landmark in hand_landmarks.landmark:
                data_aux.append(landmark.x)
                data_aux.append(landmark.y)

            prediction = self.model.predict([np.asarray(data_aux)])
            prob = self.model.predict_proba([np.asarray(data_aux)])
            predicted_character = self.labels_dict.get(np.argmax(prob), "")
            confidence_score = np.max(prob)

            return predicted_character, confidence_score, results, hand_landmarks
        return None, None, None, None

    def process_prediction(self, predicted_character, confidence_score):
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
        if self.typed_word == self.current_word:
            self.elapsed_time = time.time() - self.start_time

            if self.elapsed_time <= self.time_limit:
                self.score += 1

            self.reset_word()
            return True, self.elapsed_time
        return False, 0

    def update_timer(self):
        remaining_time = self.time_limit - (time.time() - self.start_time)
        if remaining_time <= 0:
            if self.typed_word == self.current_word:
                self.score += 1
            self.reset_word()
            return 0

        return max(0, remaining_time)

    def reset_word(self):
        time.sleep(1)
        self.current_word = random.choice(self.words)
        self.typed_word = ""
        self.start_time = time.time()
        self.elapsed_time = 0

    def get_game_state(self):
        return {
            "current_word": self.current_word,
            "typed_word": self.typed_word,
            "score": self.score,
            "remaining_time": self.update_timer()
        }