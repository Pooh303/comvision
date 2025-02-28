import customtkinter as ctk
from PIL import Image
from tkinter import ttk
from customtkinter import CTkImage
from PIL import Image, ImageTk
import tkinter as tk
import tkinter.font as tkfont


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


    # เปลี่ยนฟอนต์ตรงนี้
    def get_font(self, size=18, weight="bold"):
        # Define the default font families based on language
        family = "Sarabun"  # Thai font

        # Check if the font family exists on the system
        available_fonts = tkfont.families()
        if family not in available_fonts:
            print(f"Warning: The font '{family}' is not available. Using default font.")
            family = "Arial"  # Fallback to a default font if the chosen one is not available
        
        return ctk.CTkFont(family=family, size=size, weight=weight)


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
                                            font = ("Arial", 24), width=20, height=60)
        self.letter_combo.set("Select a Letter")
        self.letter_combo.grid(row=2, column=0, columnspan=2, pady=10)
        self.letter_combo.bind("<<ComboboxSelected>>", self.on_letter_selected)
        
        # สร้าง back_button
        back_button = ctk.CTkButton(
            content_frame, text="⬅️Back", command=self.show_welcome_screen,
            font = self.get_font(20, "bold"),
            fg_color="#ff5722", width=100, height=40
        )
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

        # Left frame content (video, word, and input)
        self.lbl_video = ctk.CTkLabel(left_frame, text="", fg_color="black", corner_radius=10, width=800, height=600)
        self.lbl_video.pack(fill="both", expand=True)

        self.lbl_word = tk.Text(left_frame, font=("Arial", 24), width=20, height=1, wrap="none", bg="black", fg="white", bd=0)
        self.lbl_word.pack(pady=10)
        self.lbl_word.tag_configure("typed", foreground="green")
        self.lbl_word.tag_configure("remaining", foreground="white")

        self.lbl_typed = ctk.CTkLabel(left_frame, text="Your Input: ", font=("Arial", 24))
        self.lbl_typed.pack(pady=10)

        # Right frame content (game stats and prediction)
        ctk.CTkLabel(right_frame, text="Game Stats", font=("Arial", 24, "bold")).pack(pady=20)

        self.lbl_result = ctk.CTkLabel(right_frame, text="Prediction: ", font=("Arial", 20))
        self.lbl_result.pack(pady=10)

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
        current_word = game_state["current_word"]
        typed_word = game_state["typed_word"]

        # แบ่งคำเป็น 2 ส่วน: ที่พิมพ์แล้ว (สีเขียว) + ที่เหลือ (สีขาว)
        typed_part = typed_word
        remaining_part = current_word[len(typed_word):]

        # ล้างข้อความเก่าออกก่อน
        self.lbl_word.config(state="normal")  # เปิดให้แก้ไขได้ชั่วคราว
        self.lbl_word.delete("1.0", "end")

        # ✅ ใส่ "📌 Word: " ขึ้นต้น
        word_prefix = "📌 Word: "
        self.lbl_word.insert("1.0", word_prefix)
        self.lbl_word.tag_add("word_label", "1.0", f"1.{len(word_prefix)}")

        # ✅ ใส่ข้อความที่พิมพ์แล้วเป็นสีเขียว
        start_index = f"1.{len(word_prefix)}"
        self.lbl_word.insert(start_index, typed_part)
        self.lbl_word.tag_add("typed", start_index, f"1.{len(word_prefix) + len(typed_part)}")

        # ✅ ใส่ข้อความที่เหลือเป็นสีขาว (ถ้ายังมี)
        start_remaining = f"1.{len(word_prefix) + len(typed_part)}"
        self.lbl_word.insert(start_remaining, remaining_part)
        self.lbl_word.tag_add("remaining", start_remaining, "end")

        # ✅ ลบพื้นหลัง + ขอบทั้งหมด
        self.lbl_word.config(
            bg=self.root.cget("bg"),  # ให้สีพื้นหลังตรงกับหน้าต่างหลัก
            borderwidth=0,
            highlightthickness=0,
            state="disabled"  # ป้องกันผู้ใช้แก้ไขเอง
        )

        # อัปเดตสีข้อความ
        self.lbl_word.tag_configure("word_label", foreground="white")  # "Word: " เป็นสีขาว
        self.lbl_word.tag_configure("typed", foreground="green")  # ตัวพิมพ์แล้วเป็นสีเขียว
        self.lbl_word.tag_configure("remaining", foreground="white")  # ตัวที่เหลือเป็นสีขาว

        # ✅ อัปเดต Your Input ให้ทันคำสุดท้ายก่อนเปลี่ยน
        self.lbl_typed.configure(text=f"📝 Your Input: {typed_word}")
        self.lbl_time.configure(text=f"⏳ Time: {game_state['remaining_time']:.2f} sec")
        self.lbl_score.configure(text=f"🏆 Score: {game_state['score']}")
        self.lbl_result.configure(text=f"🔍 {prediction_text}")

        # ✅ ถ้าพิมพ์ถูกทั้งหมดแล้ว → แสดงสีเขียวเต็มก่อน 1 วินาที → แล้วเปลี่ยนคำ
        if typed_word == current_word:
            def show_full_green():
                self.lbl_word.config(state="normal")
                self.lbl_word.tag_add("typed", "1.0", "end")  # เปลี่ยนทั้งคำให้เป็นสีเขียว
                self.lbl_word.config(state="disabled")

                self.lbl_typed.configure(text=f"📝 Your Input: {typed_word}")  # อัปเดตให้โชว์คำสุดท้าย

                self.root.after(1000, self.controller.next_word)  # Delay 1 วินาทีแล้วเปลี่ยนคำถัดไป

            self.root.after(100, show_full_green)  # รอ 100ms ก่อนทำให้ทั้งหมดเป็นสีเขียว


    def start(self):
        self.root.mainloop()