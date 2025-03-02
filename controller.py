import cv2
from model import SignLanguageModel
from model2 import SignLanguageModel2
# Import necessary components from view.py
from view import SignLanguageView  # Import the class itself
from customtkinter import CTkImage  # Import CTkImage
import customtkinter as ctk
import mediapipe as mp
from PIL import Image, ImageTk  # No ImageDraw needed in controller


class SignLanguageController:
    def __init__(self):
        self.model = SignLanguageModel()
        self.model2 = SignLanguageModel2()
        self.root = ctk.CTk()
        self.view = SignLanguageView(self.root, self)  # Keep the view reference
        self.cap = None
        self.cap2 = None

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

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame, confirmed_prediction = self.model2.predict_and_draw(frame_rgb)
        self.view.update_tutorial_frame(frame, confirmed_prediction)
        self.view.video_frame.after(50, self.update_frame_tutorial)  # Reduce frame rate

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


        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        predicted_character, confidence_score, results, hand_landmarks = self.model.predict(frame)
        self.view.update_frame(frame_rgb)

        if predicted_character is not None:
            prediction_text = f"Prediction: {predicted_character} ({confidence_score * 100:.2f}%)"
        else:
            prediction_text = "Prediction: "

        self.model.process_prediction(predicted_character, confidence_score)
        self.model.check_word_completion()
        self.model.update_timer()
        game_state = self.model.get_game_state()

        self.view.update_labels(game_state, prediction_text)
        self.view.lbl_video.after(50, self.update_frame)  # Reduce frame rate

    def start_video_example(self, name):
        """เปิดวิดีโอจากพาธที่กำหนด"""
        video_path = f"vids/{name}.mp4"

        if hasattr(self, "cap2") and self.cap2 is not None:
            self.cap2.release()
            self.cap2 = None

        self.cap2 = cv2.VideoCapture(video_path)

        if not self.cap2.isOpened():
            print(f"Error: ไม่สามารถเปิดไฟล์ {video_path} ได้")
            return

        self.update_frame_example()

    def update_frame_example(self):
        """Updates the example video frame, applying rounding AND resizing."""
        if self.cap2 is None:
            return

        ret, frame = self.cap2.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # --- Resize BEFORE applying rounding ---
            frame = cv2.resize(frame, (500, 375))  # Resize to the target size

            # --- Apply rounding AFTER resizing ---
            rounded_img = self.view._round_image(frame, (500, 375))  # Use _round_image!
            imgtk = CTkImage(light_image=rounded_img, dark_image=rounded_img, size=(500,375))

            self.view.video_frame2.configure(image=imgtk)
            self.view.video_frame2.imgtk = imgtk  # Keep the reference

            self.view.video_frame2.after(50, self.update_frame_example)  # Adjust delay
        else:
            if self.cap2:
                self.cap2.release()
            self.cap2 = None
    def run(self):
        self.view.start()
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()