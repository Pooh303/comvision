import cv2
from model import SignLanguageModel
from model2 import SignLanguageModel2
from view import SignLanguageView
import customtkinter as ctk
import cv2
import mediapipe as mp
from PIL import Image, ImageTk

class SignLanguageController:
    def __init__(self):
        self.model = SignLanguageModel()
        self.model2 = SignLanguageModel2()
        self.root = ctk.CTk()
        self.view = SignLanguageView(self.root, self)
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

        # (ถ้าต้องการแปลงเป็น RGB สามารถทำได้ แต่ในกรณีนี้เราใช้ cv2.imshow หรืออัปเดต UI ที่รองรับ BGR ก็ได้)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # เรียกใช้ฟังก์ชัน predict_and_draw จากโมเดล
        # สมมติว่า self.model เป็น instance ของ SignLanguageModel2
        frame, confirmed_prediction = self.model2.predict_and_draw(frame_rgb)

        # อัปเดตเฟรมใน UI (ในที่นี้ใช้ self.view.update_tutorial_frame)
        self.view.update_tutorial_frame(frame, confirmed_prediction)
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

    def start_video_example(self, name):
        """เปิดวิดีโอจากพาธที่กำหนด"""
        video_path = f"vids/{name}.mp4"

    # ปิด VideoCapture ตัวเก่าถ้ามี
        if hasattr(self, "cap2") and self.cap2 is not None:
            self.cap2.release()
            self.cap2 = None

        # เปิดวิดีโอใหม่
        self.cap2 = cv2.VideoCapture(video_path)

        if not self.cap2.isOpened():
            print(f"Error: ไม่สามารถเปิดไฟล์ {video_path} ได้")
            return

        self.update_frame_example()

    def update_frame_example(self):
        """อัปเดตเฟรมจากวิดีโอไปยัง CTkLabel โดยรักษาอัตราส่วนภาพ"""
        if self.cap2 is None:
            return

        ret, frame = self.cap2.read()
        if ret:
            # แปลง BGR เป็น RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # ดึงขนาดของ video_frame2
            frame_width = self.view.video_frame2.winfo_width()
            frame_height = self.view.video_frame2.winfo_height()

            # ป้องกันปัญหาขนาดเป็น 0
            if frame_width == 1 or frame_height == 1:
                self.view.video_frame2.after(10, self.update_frame_example)
                return

            # คำนวณขนาดใหม่ให้พอดีกับกรอบ โดยรักษาอัตราส่วนเดิม
            h, w, _ = frame.shape
            aspect_ratio = w / h

            if frame_width / frame_height > aspect_ratio:
                new_height = frame_height
                new_width = int(frame_height * aspect_ratio)
            else:
                new_width = frame_width
                new_height = int(frame_width / aspect_ratio)

            # Resize ภาพให้พอดีโดยไม่บิดเบี้ยว
            frame_resized = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

            # แปลงภาพให้เป็นรูปแบบที่ใช้กับ CTkLabel
            image = Image.fromarray(frame_resized)
            imgtk = ImageTk.PhotoImage(image=image)

            # อัปเดตภาพใน video_frame2
            self.view.video_frame2.configure(image=imgtk)
            self.view.video_frame2.image = imgtk  # ต้องเก็บ reference ไม่ให้ garbage collector ลบ

            # เรียกตัวเองใหม่เพื่ออัปเดตเฟรมถัดไป
            self.view.video_frame2.after(33, self.update_frame_example)  # ประมาณ 30 FPS
        else:
            self.cap2.release()
            self.cap2 = None  # เคลียร์ค่าหลังจากเล่นจบ




    def on_letter_selected(self, event):
        selected_letter = event.widget.get()
        print(f"Selected letter: {selected_letter}")
        # ประมวลผลตามที่ต้องการหลังจากเลือก letter
    def run(self):
        self.view.start()
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
