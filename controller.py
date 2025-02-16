# controller.py (Modified)
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
        self.cap = cv2.VideoCapture(1)
        self.update_frame()

    def update_frame(self):
        if self.cap is None:
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        # Convert to RGB *before* processing or drawing
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        predicted_character, confidence_score, results, hand_landmarks = self.model.predict(frame)

        # Draw landmarks *before* converting to CTkImage
        # if results and results.multi_hand_landmarks:
        #     self.view.draw_landmarks(frame_rgb, hand_landmarks)  # Pass frame_rgb here
            
        # Convert to CTkImage for display
        self.view.update_frame(frame_rgb)


        if predicted_character is not None:
              prediction_text = f"Prediction: {predicted_character} ({confidence_score * 100:.2f}%)"
        else:
            prediction_text = "Prediction: "

        self.model.process_prediction(predicted_character, confidence_score)
        self.model.check_word_completion()
        self.model.update_timer()
        game_state = self.model.get_game_state()

        # Update the View
        self.view.update_labels(game_state, prediction_text)


        self.view.lbl_video.after(10, self.update_frame)

    def run(self):
        self.view.start()
        if self.cap:
          self.cap.release()
        cv2.destroyAllWindows()