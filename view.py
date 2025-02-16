# view.py (Modified)
import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage


class SignLanguageView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.geometry("1000x700")
        self.root.title("Sign Language Recognition")

        self.lbl_video = ctk.CTkLabel(root)
        self.lbl_video.pack()

        self.lbl_result = ctk.CTkLabel(root, text="Prediction: ", font=("Arial", 24))
        self.lbl_result.pack(pady=10)

        self.lbl_word = ctk.CTkLabel(root, text=f"Word: ", font=("Arial", 20))
        self.lbl_word.pack()

        self.lbl_typed = ctk.CTkLabel(root, text=f"Your Input: ", font=("Arial", 20))
        self.lbl_typed.pack()

        self.lbl_time = ctk.CTkLabel(root, text=f"Time: ", font=("Arial", 18))
        self.lbl_time.pack()

        self.lbl_score = ctk.CTkLabel(root, text=f"Score: ", font=("Arial", 18))
        self.lbl_score.pack()

        self.btn_exit = ctk.CTkButton(root, text="Exit", command=root.quit)
        self.btn_exit.pack(pady=10)

    def update_frame(self, frame):
        img = Image.fromarray(frame)
        img_ctk = CTkImage(light_image=img, dark_image=img, size=(640, 480))
        self.lbl_video.configure(image=img_ctk)
        self.lbl_video.imgtk = img_ctk  # Prevent garbage collection


    # def draw_landmarks(self, frame, hand_landmarks):
    #       # Draw landmarks on the *original* RGB frame
    #     self.controller.model.mp_drawing.draw_landmarks(frame, hand_landmarks, self.controller.model.mp_hands.HAND_CONNECTIONS)

    def update_labels(self, game_state, prediction_text):
         self.lbl_word.configure(text=f"Word: {game_state['current_word']}")
         self.lbl_typed.configure(text=f"Your Input: {game_state['typed_word']}")
         self.lbl_time.configure(text=f"Time: {game_state['remaining_time']:.2f} sec")
         self.lbl_score.configure(text=f"Score: {game_state['score']}")
         self.lbl_result.configure(text=prediction_text)


    def start(self):
        self.controller.start_video_capture()
        self.root.mainloop()