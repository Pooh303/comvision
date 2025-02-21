import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage
from PIL import Image, ImageTk

class SignLanguageView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.geometry("1000x700")
        self.root.title("Sign Language Recognition")

        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(expand=True, fill="both")

        # แสดงหน้า Welcome ก่อน
        self.show_welcome_screen()

    def show_tutorial_screen(self):
        """ แสดงหน้า Tutorial """
        self.clear_screen()

        game_label = ctk.CTkLabel(self.main_frame, text="🎯 ตัวอย่างอักษรในภาษามือ", font=("Arial", 30, "bold"))
        game_label.grid(row=0, column=0, columnspan=10, pady=10)

        # สร้างปุ่ม A, B, C, D, E
        letters = [chr(i) for i in range(ord("A"), ord("Z") + 1)]  # สร้างอักษร A-Z
        for idx, letter in enumerate(letters):
            row, col = divmod(idx, 10)  # คำนวณแถวและคอลัมน์
            btn = ctk.CTkButton(self.main_frame, text=letter, font=("Arial", 24), width=80, height=60,
                                command=lambda l=letter: self.show_image_for_letter(l))
            btn.grid(row=row + 1, column=col, padx=5, pady=5)  # row+1 เพื่อหลีกเลี่ยงการชนกับ game_label

        # ปุ่มกลับไปหน้าหลัก
        back_button = ctk.CTkButton(self.main_frame, text="🔙 กลับหน้าหลัก", command=self.show_welcome_screen, font=("Arial", 24))
        back_button.grid(row=2, column=0, columnspan=5, pady=20, sticky="sw")

        # สร้าง Label สำหรับแสดงภาพจากกล้อง
        self.video_frame = ctk.CTkLabel(self.main_frame)
        self.video_frame.grid(row=4, column=0, columnspan=10, pady=20)

        # สร้าง Label สำหรับแสดงรูป
        self.image_label = ctk.CTkLabel(self.main_frame, text="", font=("Arial", 30, "bold"))
        self.image_label.grid(row=2, column=1, columnspan=5, pady=20, sticky="e")

        self.controller.start_video_capture_tutorial() # เริ่มจับภาพจากกล้อง

    def show_image_for_letter(self, letter):
        """ ฟังก์ชันที่แสดงภาพที่เกี่ยวข้องกับตัวอักษร """
        # โหลดรูปภาพจากไฟล์ที่เกี่ยวข้อง
        image_path = f"./images/{letter.lower()}.png"  # กำหนดเส้นทางของไฟล์รูปภาพ

        # ใช้ PIL ในการเปิดรูปภาพ
        img = Image.open(image_path)
        img = img.resize((100, 100))  # ปรับขนาดภาพให้พอดีกับ UI

        # แปลงรูปภาพให้เป็น CTkImage สำหรับ CustomTkinter
        img_ctk = CTkImage(img, size=(100, 100))  # ปรับขนาดภาพตามที่ต้องการ

        # อัปเดต image_label ด้วย CTkImage ใหม่
        self.image_label.configure(image=img_ctk)
        self.image_label.image = img_ctk  # ต้องเก็บการอ้างอิงไว้ เพื่อไม่ให้ภาพถูกลบ


    def clear_screen(self):
        """ ลบ widget ทั้งหมดใน main_frame """
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_welcome_screen(self):
        """ สร้างหน้า Welcome ก่อนเริ่มเกม """
        self.clear_screen()

        lbl_title = ctk.CTkLabel(self.main_frame, text="Sign Language Recognition", font=("Arial", 32, "bold"))
        lbl_title.grid(row=0, column=0, columnspan=3, pady=20)

        btn_start = ctk.CTkButton(self.main_frame, text="Start Game", command=self.start_game)
        btn_start.grid(row=1, column=1, pady=10, padx=10)

        btn_tutorial = ctk.CTkButton(self.main_frame, text="Tutorial", command=self.show_tutorial_screen)
        btn_tutorial.grid(row=2, column=1, pady=10, padx=10)

        btn_exit = ctk.CTkButton(self.main_frame, text="Exit", command=self.root.quit)
        btn_exit.grid(row=3, column=1, pady=10, padx=10)
      
    def start_game(self):
        """ ซ่อนหน้า Welcome แล้วแสดงหน้าเกม """
        self.clear_screen()  # ใช้ clear_screen() แทนการซ่อน frame
        self.show_game_screen()
        self.controller.start_video_capture()  # เริ่มกล้อง

    def show_game_screen(self):
        """ UI หลักของเกม """
        self.main_frame.pack_forget()  # ซ่อน main_frame เพื่อเคลียร์ UI หน้าเก่า
        
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
        self.lbl_word.configure(text=f"Word: {game_state['current_word']}")
        self.lbl_typed.configure(text=f"Your Input: {game_state['typed_word']}")
        self.lbl_time.configure(text=f"Time: {game_state['remaining_time']:.2f} sec")
        self.lbl_score.configure(text=f"Score: {game_state['score']}")
        self.lbl_result.configure(text=prediction_text)

    def start(self):
        self.root.mainloop()
