import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage


class SignLanguageView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.geometry("1000x700")
        self.root.title("Sign Language Recognition")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.main_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # แสดงหน้า Welcome ก่อน
        self.show_welcome_screen()

    def show_tutorial_screen(self):
        """ 🎯 แสดงหน้า Tutorial (ใช้ ComboBox แทนปุ่ม A-Z) """
        self.clear_screen()

        max_columns = 5  # ใช้กำหนด Grid Layout
        for i in range(max_columns):
            self.main_frame.grid_columnconfigure(i, weight=1)

        # ✅ ปุ่มกลับหน้าหลัก (ขวาบน)
        back_button = ctk.CTkButton(self.main_frame, text="🔙 กลับหน้าหลัก",
                                    command=self.show_welcome_screen, font=("Arial", 16),
                                    fg_color="#ff5722", width=100, height=40)
        back_button.grid(row=0, column=max_columns - 1, padx=10, pady=10, sticky="ne")  # อยู่ขวาบน

        # ✅ หัวข้อใหญ่อยู่ตรงกลาง
        game_label = ctk.CTkLabel(self.main_frame, text="🎯 ตัวอย่างอักษรในภาษามือ", font=("Arial", 22, "bold"))
        game_label.grid(row=1, column=0, columnspan=max_columns, pady=10, sticky="n")

        # ✅ **Video อยู่ด้านบนสุด ใต้หัวข้อ**
        self.video_frame = ctk.CTkLabel(self.main_frame, text="", fg_color="black", corner_radius=10,
                                        width=640, height=480)
        self.video_frame.grid(row=2, column=0, columnspan=max_columns, pady=20, sticky="n")

        # ✅ **เปลี่ยนจากปุ่ม A-Z เป็น ComboBox**
        self.letter_combo = ctk.CTkComboBox(self.main_frame, values=[chr(i) for i in range(65, 91)], 
                                            font=("Arial", 16), width=150, height=40)
        self.letter_combo.set("เลือกตัวอักษร")  # ค่าเริ่มต้น
        self.letter_combo.grid(row=3, column=0, columnspan=max_columns, pady=10, sticky="n")

        # ✅ ปรับ Layout ให้อยู่กลาง
        self.main_frame.grid_rowconfigure(4, weight=1)

        # ✅ เชื่อม Event เมื่อเลือกตัวอักษรจาก ComboBox
        self.letter_combo.bind("<<ComboboxSelected>>", self.on_letter_selected)
        self.controller.start_video_capture_tutorial()
    def on_letter_selected(self, event):
        """ อัปเดตค่าเมื่อเลือกตัวอักษร """
        selected_letter = self.letter_combo.get()
        print(f"เลือกตัวอักษร: {selected_letter}")


    def clear_screen(self):
        """ ลบ widget ทั้งหมดใน main_frame """
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_welcome_screen(self):
        """ สร้างหน้า Welcome ก่อนเริ่มเกม """
        self.clear_screen()

        # Center the content
        self.main_frame.columnconfigure(0, weight=1)

        lbl_title = ctk.CTkLabel(self.main_frame, text="Sign Language Recognition", font=("Arial", 32, "bold"))
        lbl_title.grid(row=0, column=0, pady=20, sticky="nsew")

        btn_start = ctk.CTkButton(self.main_frame, text="🚀 Start Game", font=("Arial", 28, "bold"),command=self.start_game)
        btn_start.grid(row=1, column=0, pady=10, padx=10, sticky="nsew")

        btn_tutorial = ctk.CTkButton(self.main_frame, text="📖 Tutorial", font=("Arial", 28, "bold"), command=self.show_tutorial_screen)
        btn_tutorial.grid(row=2, column=0, pady=10, padx=10, sticky="nsew")

        btn_exit = ctk.CTkButton(self.main_frame, text="❌ Exit", command=self.show_welcome_screen,
                                font=("Arial", 24), fg_color="#f44336", width=200)
        btn_exit.grid(row=3, column=0, pady=10, sticky="nsew")

        # Make rows expand equally for better vertical alignment
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        self.main_frame.rowconfigure(3, weight=1)


    def start_game(self):
        """ ซ่อนหน้า Welcome แล้วแสดงหน้าเกม """
        self.clear_screen()
        self.show_game_screen()
        self.controller.start_video_capture()

    def show_game_screen(self):
        """ UI หลักของเกม """
        self.main_frame.pack_forget()

        self.lbl_video = ctk.CTkLabel(self.root, text="", fg_color="black", corner_radius=10)
        self.lbl_video.pack(pady=20)

        self.lbl_result = ctk.CTkLabel(self.root, text="Prediction: ", font=("Arial", 24))
        self.lbl_result.pack(pady=10)

        self.lbl_word = ctk.CTkLabel(self.root, text="Word: ", font=("Arial", 22))
        self.lbl_word.pack(pady=5)

        self.lbl_typed = ctk.CTkLabel(self.root, text="Your Input: ", font=("Arial", 22))
        self.lbl_typed.pack(pady=5)

        self.lbl_time = ctk.CTkLabel(self.root, text="Time: ", font=("Arial", 20))
        self.lbl_time.pack(pady=5)

        self.lbl_score = ctk.CTkLabel(self.root, text="Score: ", font=("Arial", 20))
        self.lbl_score.pack(pady=5)

        self.btn_exit = ctk.CTkButton(self.root, text="❌ Exit", command=self.root.quit,
                                     fg_color="#f44336", font=("Arial", 22))
        self.btn_exit.pack(pady=20)

    def update_tutorial_frame(self, frame):
        img = Image.fromarray(frame)
        img_ctk = CTkImage(light_image=img, dark_image=img, size=(640, 480))
        self.video_frame.configure(image=img_ctk)
        self.video_frame.imgtk = img_ctk  # ป้องกัน garbage collection

    def update_frame(self, frame):
        img = Image.fromarray(frame)
        img_ctk = CTkImage(light_image=img, dark_image=img, size=(640, 480))
        self.lbl_video.configure(image=img_ctk)
        self.lbl_video.imgtk = img_ctk  # ป้องกัน garbage collection

    def update_labels(self, game_state, prediction_text):
        """ อัปเดต UI ด้วยข้อมูลใหม่ """
        self.lbl_word.configure(text=f"📌 Word: {game_state['current_word']}")
        self.lbl_typed.configure(text=f"📝 Your Input: {game_state['typed_word']}")
        self.lbl_time.configure(text=f"⏳ Time: {game_state['remaining_time']:.2f} sec")
        self.lbl_score.configure(text=f"🏆 Score: {game_state['score']}")
        self.lbl_result.configure(text=f"🔍 Prediction: {prediction_text}")

    def start(self):
        self.root.mainloop()
