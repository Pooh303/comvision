import pickle
import cv2
import mediapipe as mp
import numpy as np
import time
import math
class SignLanguageModel2:
    def __init__(self, model_path='./model_bestest.p'):
        # โหลดโมเดล
        model_dict = pickle.load(open(model_path, 'rb'))
        self.model = model_dict['model']
        self.labels_dict = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'K', 10: 'L',
                             11: 'M', 12: 'N', 13: 'O', 14: 'P', 15: 'Q', 16: 'R', 17: 'S', 18: 'T', 19: 'U', 20: 'V',
                             21: 'W', 22: 'X', 23: 'Y'}
        # ตั้งค่า Mediapipe
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.hands = self.mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.7)
        
        # ตัวแปรควบคุมการแสดงผล
        self.last_prediction = None
        self.last_prediction_time = 0
        self.confirmed_prediction = None    
        self.display_time = 0  # เวลาที่ต้องแสดงผล 3 วินาที
        self.countdown = 0  # เก็บเวลานับ 1-3 วิ

    def predict_and_draw(self, frame):
        """
        Predicts sign language letters and draws the results on the frame.

        Args:
            frame (np.ndarray): Camera frame.

        Returns:
            tuple: (frame, confirmed_prediction)
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        data_aux = []
        x_ = []
        y_ = []
        H, W, _ = frame.shape
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]  # เลือกมือแรก
            self.mp_drawing.draw_landmarks(
                frame,  # image to draw
                hand_landmarks,  # model output
                self.mp_hands.HAND_CONNECTIONS,  # hand connections
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style())
            
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y

                x_.append(x)
                y_.append(y)

            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                data_aux.append(x - min(x_))
                data_aux.append(y - min(y_))

            x1 = int(min(x_) * W) - 10
            y1 = int(min(y_) * H) - 10
            x2 = int(max(x_) * W) - 10
            y2 = int(max(y_) * H) - 10
           
            # Predict sign language character
            prediction = self.model.predict([np.asarray(data_aux)])
            prob = self.model.predict_proba([np.asarray(data_aux)])
            predicted_proba = np.max(prob)
            predicted_character = self.labels_dict[int(prediction[0])]

            # แสดงกรอบรอบมือ
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
            cv2.putText(frame, f'{predicted_character}: {predicted_proba:.2f}', 
                        (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        1.3, (0, 0, 0), 3, cv2.LINE_AA)

            # อัปเดตค่าพยากรณ์
            self.update_prediction(predicted_character, predicted_proba)

        # แสดงเวลานับถอยหลัง 1-3 วินาที
        if self.countdown > 0 and self.countdown < 3:
            cv2.putText(frame, f"Confirming in: {self.countdown}", 
                        (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 4, cv2.LINE_AA)

        # แสดงตัวอักษรที่ยืนยันแล้วค้างไว้ 3 วินาที
        if self.confirmed_prediction and time.time() - self.display_time < 3:
            cv2.putText(frame, f"{self.confirmed_prediction}",
                        (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4, cv2.LINE_AA)

        return frame, self.confirmed_prediction


    def update_prediction(self, predicted_character, confidence_score):
        """
        Updates the predicted letter with confirmation.

        Args:
            predicted_character (str): Predicted letter.
            confidence_score (float): Confidence score.
        """       
        current_time = time.time()

        if confidence_score > 0.60:  # ค่าความแม่นยำต้องมากกว่า 60%
            if predicted_character == self.last_prediction:
                elapsed_time = current_time - self.last_prediction_time
                self.countdown = math.ceil(elapsed_time)  # ใช้ math.ceil เพื่อให้ขึ้นเลขถัดไปชัวร์

                if elapsed_time >= 2:  # ต้องค้างไว้อย่างน้อย 2 วินาที
                    self.confirmed_prediction = predicted_character
                    self.display_time = current_time  # เริ่มจับเวลาแสดงผล 3 วิ
                    self.countdown = 0  # รีเซ็ตเวลานับถอยหลัง
            else:
                self.last_prediction = predicted_character
                self.last_prediction_time = current_time
                self.countdown = 0  # รีเซ็ตเวลานับถอยหลัง
        else:
            self.last_prediction = None
            self.last_prediction_time = 0
            self.countdown = 0
