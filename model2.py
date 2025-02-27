import pickle
import cv2
import mediapipe as mp
import numpy as np
import time

class SignLanguageModel2:
    def __init__(self, model_path='./model.p'):
        # โหลดโมเดล
        model_dict = pickle.load(open(model_path, 'rb'))
        self.model = model_dict['model']
        self.labels_dict = {0: 'A', 1: 'B', 2:'L', 3:'C'}

        # ตั้งค่า Mediapipe
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.8)

        self.last_prediction = None
        self.last_prediction_time = 0
        self.confirmed_prediction = None
    def predict_and_draw(self, frame):
        """ พยากรณ์และวาดผลลัพธ์ลงบน frame """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # วาดโครงร่างมือ
                self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                # เตรียมข้อมูลพยากรณ์
                data_aux = []
                x_ = []
                y_ = []

                for landmark in hand_landmarks.landmark:
                    x = landmark.x
                    y = landmark.y
                    data_aux.append(x)
                    data_aux.append(y)
                    x_.append(x)
                    y_.append(y)

                # พยากรณ์
                prediction = self.model.predict([np.asarray(data_aux)])
                prob = self.model.predict_proba([np.asarray(data_aux)])

                predicted_character = self.labels_dict.get(np.argmax(prob), "")
                confidence_score = np.max(prob)
                self.update_prediction(predicted_character, confidence_score)
                # หาตำแหน่งของมือเพื่อนำไปใช้วาดกรอบ
                x1 = int(min(x_) * frame.shape[1]) - 10
                y1 = int(min(y_) * frame.shape[0]) - 10
                x2 = int(max(x_) * frame.shape[1]) - 10
                y2 = int(max(y_) * frame.shape[0]) - 10

                # วาดกรอบรอบมือ 
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)

                # แสดงอักษรที่พยากรณ์ได้
                if self.confirmed_prediction:
                    cv2.putText(frame, f"{self.confirmed_prediction}",
                                (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)
                else:
                    cv2.putText(frame, f"{predicted_character} ({confidence_score:.2f})",
                                (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)

        return frame, self.confirmed_prediction
    
    def update_prediction(self, predicted_character, confidence_score):
        """ ตรวจสอบค่าพยากรณ์และยืนยันผลเมื่อเงื่อนไขครบ """
        current_time = time.time()

        if confidence_score > 0.80:  # ค่าความแม่นยำต้องเกิน 80%
            if predicted_character == self.last_prediction:
                if current_time - self.last_prediction_time >= 3:  # ต้องค้างไว้นาน 3 วิ
                    self.confirmed_prediction = predicted_character
            else:
                self.last_prediction = predicted_character
                self.last_prediction_time = current_time
        else:
            self.last_prediction = None
            self.last_prediction_time = 0
            self.confirmed_prediction = None