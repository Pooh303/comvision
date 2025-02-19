import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage


class SignLanguageView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.geometry("1000x700")
        self.root.title("Sign Language Recognition")

        # เรียกหน้า Welcome ก่อน
        self.show_welcome_screen()

    def show_welcome_screen(self):
        """ สร้างหน้า Welcome ก่อนเริ่มเกม """
        self.welcome_frame = ctk.CTkFrame(self.root)
        self.welcome_frame.pack(expand=True, fill="both")

        lbl_title = ctk.CTkLabel(self.welcome_frame, text="Sign Language Recognition", font=("Arial", 32, "bold"))
        lbl_title.pack(pady=20)

        btn_start = ctk.CTkButton(self.welcome_frame, text="Start Game", command=self.start_game)
        btn_start.pack(pady=10)

        btn_exit = ctk.CTkButton(self.welcome_frame, text="Exit", command=self.root.quit)
        btn_exit.pack(pady=10)

    def start_game(self):
        """ ซ่อนหน้า Welcome แล้วแสดงหน้าเกม """
        self.welcome_frame.pack_forget()  # ซ่อนหน้า Welcome
        self.show_game_screen()
        self.controller.start_video_capture()  # เริ่มกล้อง

    def show_game_screen(self):
        """ UI หลักของเกม """
        self.lbl_video = ctk.CTkLabel(self.root)
        self.lbl_video.pack()

        self.lbl_result = ctk.CTkLabel(self.root, text="Prediction: ", font=("Arial", 24))
        self.lbl_result.pack(pady=10)

        self.lbl_word = ctk.CTkLabel(self.root, text="Word: ", font=("Arial", 20))
        self.lbl_word.pack()

        self.lbl_typed = ctk.CTkLabel(self.root, text="Your Input: ", font=("Arial", 20))
        self.lbl_typed.pack()

        self.lbl_time = ctk.CTkLabel(self.root, text="Time: ", font=("Arial", 18))
        self.lbl_time.pack()

        self.lbl_score = ctk.CTkLabel(self.root, text="Score: ", font=("Arial", 18))
        self.lbl_score.pack()

        self.btn_exit = ctk.CTkButton(self.root, text="Exit", command=self.root.quit)
        self.btn_exit.pack(pady=10)

    def update_frame(self, frame):
        img = Image.fromarray(frame)
        img_ctk = CTkImage(light_image=img, dark_image=img, size=(640, 480))
        self.lbl_video.configure(image=img_ctk)
        self.lbl_video.imgtk = img_ctk  # ป้องกัน garbage collection

    def update_labels(self, game_state, prediction_text):
        self.lbl_word.configure(text=f"Word: {game_state['current_word']}")
        self.lbl_typed.configure(text=f"Your Input: {game_state['typed_word']}")
        self.lbl_time.configure(text=f"Time: {game_state['remaining_time']:.2f} sec")
        self.lbl_score.configure(text=f"Score: {game_state['score']}")
        self.lbl_result.configure(text=prediction_text)

    def start(self):
        self.root.mainloop()
