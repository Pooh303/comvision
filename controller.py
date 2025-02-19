import cv2
from model import SignLanguageModel
from view import SignLanguageView
import customtkinter as ctk


class SignLanguageController:
    def __init__(self):
        self.model = SignLanguageModel()
        self.root = ctk.CTk()
        self.view = SignLanguageView(self.root, self)
        self.cap = None

    def start_video_capture(self):
        """ เริ่มต้นเปิดกล้อง """
        self.cap = cv2.VideoCapture(1)
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
