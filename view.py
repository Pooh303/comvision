import customtkinter as ctk
from PIL import Image
from tkinter import ttk
from customtkinter import CTkImage
from PIL import Image, ImageTk
class SignLanguageView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.geometry("1200x1000")
        self.root.title("Sign Language Recognition")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.main_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.show_welcome_screen()

    def show_tutorial_screen(self):
        self.clear_screen()

        # สร้าง content_frame ซึ่งจะใช้ grid ในการจัดตำแหน่ง
        content_frame = ctk.CTkFrame(self.main_frame)
        content_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # สร้าง grid layout ให้ widget อยู่ในตำแหน่งที่ต้องการ
        title_label = ctk.CTkLabel(content_frame, text="🎯 Sign Language Alphabet", font=("Arial", 28, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=20)

        # สร้าง video_frame 1
        self.video_frame = ctk.CTkLabel(content_frame, text="", fg_color="black", corner_radius=10,
                                        width=500, height=375)
        self.video_frame.grid(row=1, column=0, padx=10, pady=20)

        # สร้าง video_frame 2
        self.video_frame2 = ctk.CTkLabel(content_frame, text="", fg_color="black", corner_radius=10,
                                        width=500, height=375)
        self.video_frame2.grid(row=1, column=1, padx=10, pady=20)

        # สร้าง ComboBox
        self.letter_combo = ttk.Combobox(content_frame, values=[chr(i) for i in range(65, 91)], 
                                            font=("Arial", 18), width=20, height=40)
        self.letter_combo.set("Select a Letter")
        self.letter_combo.grid(row=2, column=0, columnspan=2, pady=20)
        self.letter_combo.bind("<<ComboboxSelected>>", self.on_letter_selected)
        # สร้าง back_button
        back_button = ctk.CTkButton(content_frame, text="🔙 Back to Home", command=self.show_welcome_screen, 
                                    font=("Arial", 16), fg_color="#ff5722", width=200, height=40)
        back_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        self.controller.start_video_capture_tutorial()

    def on_letter_selected(self, event):
        selected_letter = self.letter_combo.get()
        print(f"Selected letter: {selected_letter}")
        self.controller.start_video_example(selected_letter)


    def clear_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_welcome_screen(self):
        self.clear_screen()

        welcome_frame = ctk.CTkFrame(self.main_frame, corner_radius=15)
        welcome_frame.pack(expand=True, fill="both", padx=40, pady=40)

        lbl_title = ctk.CTkLabel(welcome_frame, text="Sign Language Recognition", 
                                 font=("Arial", 40, "bold"))
        lbl_title.pack(pady=40)

        btn_start = ctk.CTkButton(welcome_frame, text="🚀 Start Game", command=self.start_game,
                                  font=("Arial", 20), width=250, height=50)
        btn_start.pack(pady=20)

        btn_tutorial = ctk.CTkButton(welcome_frame, text="📖 Tutorial", command=self.show_tutorial_screen,
                                     font=("Arial", 20), width=250, height=50)
        btn_tutorial.pack(pady=20)

        btn_exit = ctk.CTkButton(welcome_frame, text="❌ Exit", command=self.root.quit,
                                 font=("Arial", 20), fg_color="#f44336", width=250, height=50)
        btn_exit.pack(pady=20)

    def start_game(self):
        self.clear_screen()
        self.show_game_screen()
        self.controller.start_video_capture()

    def show_game_screen(self):
        game_frame = ctk.CTkFrame(self.main_frame, corner_radius=15)
        game_frame.pack(expand=True, fill="both", padx=20, pady=20)

        left_frame = ctk.CTkFrame(game_frame, corner_radius=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        right_frame = ctk.CTkFrame(game_frame, corner_radius=10, width=300)
        right_frame.pack(side="right", fill="y", padx=10, pady=10)

        # Left frame content (video and prediction)
        self.lbl_video = ctk.CTkLabel(left_frame, text="", fg_color="black", corner_radius=10)
        self.lbl_video.pack(pady=20, padx=20, fill="both", expand=True)

        self.lbl_result = ctk.CTkLabel(left_frame, text="Prediction: ", font=("Arial", 24))
        self.lbl_result.pack(pady=10)

        # Right frame content (game stats)
        ctk.CTkLabel(right_frame, text="Game Stats", font=("Arial", 24, "bold")).pack(pady=20)

        self.lbl_word = ctk.CTkLabel(right_frame, text="Word: ", font=("Arial", 20))
        self.lbl_word.pack(pady=10)

        self.lbl_typed = ctk.CTkLabel(right_frame, text="Your Input: ", font=("Arial", 20))
        self.lbl_typed.pack(pady=10)

        self.lbl_time = ctk.CTkLabel(right_frame, text="Time: ", font=("Arial", 18))
        self.lbl_time.pack(pady=10)

        self.lbl_score = ctk.CTkLabel(right_frame, text="Score: ", font=("Arial", 18))
        self.lbl_score.pack(pady=10)

        self.btn_exit = ctk.CTkButton(right_frame, text="❌ Exit", command=self.show_welcome_screen,
                                      fg_color="#f44336", font=("Arial", 18), width=200)
        self.btn_exit.pack(pady=20)

    def update_tutorial_frame(self, frame, confirmed_prediction):
        img = Image.fromarray(frame)
        img_ctk = CTkImage(light_image=img, dark_image=img, size=(500, 375))
        self.video_frame.configure(image=img_ctk)
        self.video_frame.imgtk = img_ctk


        current_value = self.letter_combo.get()
        if current_value == "Select a Letter" and confirmed_prediction is not None:
            values = [chr(i) for i in range(65, 91)]  # ค่า A ถึง Z

            # ตรวจสอบว่ามี confirmed_prediction และอัปเดตค่าใน ComboBox
            if confirmed_prediction is not None:
                confirmed_letter = str(confirmed_prediction)  # แปลงเป็นตัวอักษร
                if confirmed_letter in values:
                    current_index = values.index(confirmed_letter)
                    next_index = (current_index + 1) % len(values)  # วนกลับที่ A ถ้าถึง Z
                    self.letter_combo.set(values[next_index])  # ตั้งค่าตัวอักษรถัดไป
                    self.on_letter_selected(None)  
        if confirmed_prediction is not None and str(confirmed_prediction) == current_value:
                # ดึงค่าทั้งหมดจาก ComboBox (A-Z)
                values = [chr(i) for i in range(65, 91)]  # ["A", "B", ..., "Z"]
                
                # หา index ของค่าปัจจุบัน
                if current_value in values:
                    current_index = values.index(current_value)
                    
                    # หา index ของค่าถัดไป
                    next_index = (current_index + 1) % len(values)  # วนกลับไปที่ A ถ้าถึง Z
                    
                    # อัปเดตค่าใน ComboBox
                    self.letter_combo.set(values[next_index])
                    self.on_letter_selected(None)  

        else:
            pass
    
    def update_viedo_example(self, frame):
        img = Image.fromarray(frame)
        img_ctk = CTkImage(light_image=img, dark_image=img, size=(640, 480))
        self.video_frame2.configure(image=img_ctk)
        self.video_frame2.imgtk = img_ctk

    def update_frame(self, frame):
        img = Image.fromarray(frame)
        img_ctk = CTkImage(light_image=img, dark_image=img, size=(640, 480))
        self.lbl_video.configure(image=img_ctk)
        self.lbl_video.imgtk = img_ctk

    def update_labels(self, game_state, prediction_text):
        self.lbl_word.configure(text=f"📌 Word: {game_state['current_word']}")
        self.lbl_typed.configure(text=f"📝 Your Input: {game_state['typed_word']}")
        self.lbl_time.configure(text=f"⏳ Time: {game_state['remaining_time']:.2f} sec")
        self.lbl_score.configure(text=f"🏆 Score: {game_state['score']}")
        self.lbl_result.configure(text=f"🔍 Prediction: {prediction_text}")

    def start(self):
        self.root.mainloop()