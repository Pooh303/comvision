import cv2
from model import SignLanguageModel
from model2 import SignLanguageModel2
from view import SignLanguageView
import customtkinter as ctk
import cv2
import mediapipe as mp

class SignLanguageController:
    def __init__(self):
        self.model = SignLanguageModel()
        self.model2 = SignLanguageModel2()
        self.root = ctk.CTk()
        self.view = SignLanguageView(self.root, self)
        self.cap = None

    def start_video_capture_tutorial(self):
        """ เริ่มต้นเปิดกล้อง """
        self.cap = cv2.VideoCapture(0)
        self.update_frame_tutorial()

    

    def update_frame_tutorial(self):
        if self.cap is None:
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        # (ถ้าต้องการแปลงเป็น RGB สามารถทำได้ แต่ในกรณีนี้เราใช้ cv2.imshow หรืออัปเดต UI ที่รองรับ BGR ก็ได้)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # เรียกใช้ฟังก์ชัน predict_and_draw จากโมเดล
        # สมมติว่า self.model เป็น instance ของ SignLanguageModel2
        frame = self.model2.predict_and_draw(frame_rgb)

        # อัปเดตเฟรมใน UI (ในที่นี้ใช้ self.view.update_tutorial_frame)
        self.view.update_tutorial_frame(frame)

        # เรียกฟังก์ชันซ้ำหลัง 10 มิลลิวินาที
        self.view.video_frame.after(10, self.update_frame_tutorial)


    def start_video_capture(self):
        """ เริ่มต้นเปิดกล้อง """
        self.cap = cv2.VideoCapture(0)
        self.update_frame()

    def update_frame(self):
        """ อัพเดตภาพจากกล้อง """
        if self.cap is None:
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        # Convert to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Predict hand sign
        predicted_character, confidence_score, results, hand_landmarks = self.model.predict(frame)

        # Convert to CTkImage
        self.view.update_frame(frame_rgb)

        # อัพเดตข้อความผลลัพธ์
        if predicted_character is not None:
            prediction_text = f"Prediction: {predicted_character} ({confidence_score * 100:.2f}%)"
        else:
            prediction_text = "Prediction: "

        # อัพเดตข้อมูลเกม
        self.model.process_prediction(predicted_character, confidence_score)
        self.model.check_word_completion()
        self.model.update_timer()
        game_state = self.model.get_game_state()

        # ส่งค่าไปแสดงผล
        self.view.update_labels(game_state, prediction_text)

        self.view.lbl_video.after(10, self.update_frame)

    def run(self):
        self.view.start()
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
