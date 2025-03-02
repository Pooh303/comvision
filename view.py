# view.py
import tkinter as tk
import tkinter.font as tkfont
import customtkinter as ctk
from customtkinter import CTkImage
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw  # Import ImageDraw

# Hiding warnings
import warnings
warnings.filterwarnings("ignore")

class SignLanguageView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        # ตั้งค่าขนาดหน้าต่าง
        window_width = 1280
        window_height = 720
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)

        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.root.title("Sign Language Recognition")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.main_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.main_frame.pack(expand=True, fill="both")

        # --- Store base font settings ---
        self.base_font_family = "Quicksand"
        self.base_font_size = 40
        self.base_font_weight = "bold"

        # --- Load the custom font (using CTkFont) for most widgets---
        try:
            self.custom_font = ctk.CTkFont(family="Quicksand", size=40, weight="bold")
        except tk.TclError:
            print("Error: Could not load custom font 'Quicksand'.")
            print("Falling back to Arial.")
            self.custom_font = ctk.CTkFont(family="Arial", size=40, weight="bold")

        # --- Create a separate tkinter.font.Font for the Combobox ---
        try:
            # self.combobox_font = tkfont.Font(family="Quicksand", size=24, weight="bold")
            self.combobox_font = tkfont.Font(family=self.base_font_family, size=16, weight=self.base_font_weight)
            self.combobox_font.actual()  # Check if font loaded
        except tk.TclError:
            print("Error: Could not load font for Combobox.  Falling back to Arial.")
            self.combobox_font = tkfont.Font(family="Arial", size=24, weight="bold")

        self.show_welcome_screen()


    def set_font(self, family="Arial", size=20, weight="bold"):
        try:
            font = ctk.CTkFont(family=family, size=size, weight=weight)
            return font
        except tk.TclError:
            print(f"Error: Could not create font with family '{family}'. Falling back to Arial.")
            return ctk.CTkFont(family="Arial", size=size, weight=weight) #return CTkFont


    def show_welcome_screen(self):
        self.clear_screen()
        welcome_frame = ctk.CTkFrame(self.main_frame)
        welcome_frame.pack(expand=True, fill="both")

        if ctk.get_appearance_mode() == "Dark":
            bg_color = welcome_frame.cget("fg_color")[1]
        else:
            bg_color = welcome_frame.cget("fg_color")[0]

        lbl_title = tk.Text(welcome_frame, font=self.set_font("Quicksand", 60, "bold"), height=1, width=15, wrap="none", 
                            bg=bg_color, bd=0, highlightthickness=0)
        lbl_title.pack(pady=40)

        # full_text = "Sign Language Recognition"
        full_text = "Alpha Signing Test"
        lbl_title.insert("end", full_text)
        lbl_title.tag_add("green_letters", "1.0", "1.1")
        lbl_title.tag_add("green_letters", "1.6", "1.7")
        lbl_title.tag_add("green_letters", "1.14", "1.15")
        lbl_title.tag_configure("green_letters", foreground="green")

        green_indices = [(0, 1), (6, 7), (14, 15)]
        start = 0
        for green_start, green_end in green_indices:
            if start < green_start:
                lbl_title.tag_add("white_letters", f"1.{start}", f"1.{green_start}")
            start = green_end
        if start < len(full_text):
            lbl_title.tag_add("white_letters", f"1.{start}", f"1.{len(full_text)}")

        lbl_title.tag_configure("white_letters", foreground="white")
        lbl_title.config(state="disabled")

        btn_start = ctk.CTkButton(welcome_frame, text="🚀 Start Game", command=self.start_game, font=self.set_font("Quicksand", 25, "bold"), fg_color="green", width=260, height=70, corner_radius=25)
        btn_start.pack(pady=20)
        btn_tutorial = ctk.CTkButton(welcome_frame, text="📖 Tutorial", command=self.show_tutorial_screen, font=self.set_font("Quicksand", 25, "bold"), 
                                     fg_color="#2196f3", width=260, height=70, corner_radius=25)
        btn_tutorial.pack(pady=20)
        btn_exit = ctk.CTkButton(welcome_frame, text="❌ Exit", command=self.root.quit, font=self.set_font("Quicksand", 25, "bold"), fg_color="#f44336", width=260, height=70, corner_radius=25)
        btn_exit.pack(pady=20)

    # กดเริ่มเกม
    def start_game(self):
        self.clear_screen()
        self.show_game_screen()
        self.controller.start_video_capture()


    def show_game_screen(self):
        # หน้าจอเกม
        game_frame = ctk.CTkFrame(self.main_frame)
        game_frame.pack(expand=True, fill="both")

        # เฟรมฝั่งซ้าย
        left_frame = ctk.CTkFrame(game_frame, corner_radius=10)
        left_frame.pack(side="left", expand=True, padx=10, pady=10)

        # กล้อง
        self.lbl_video = ctk.CTkLabel(left_frame, text="",  corner_radius=20, width=640, height=480)
        self.lbl_video.pack(expand=True, pady=20)

        # เฟรมฝั่งขวา
        right_frame = ctk.CTkFrame(game_frame, corner_radius=10)
        right_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        # อินพุตของผู้เล่น
        self.lbl_word = tk.Text(left_frame, font=self.set_font("Quicksand", 30, "bold"), width=20, height=1, wrap="none", bg="black", fg="white")
        self.lbl_word.pack(pady=0)
        self.lbl_word.tag_configure("typed", foreground="green")
        self.lbl_word.tag_configure("remaining", foreground="white")

        self.lbl_typed = ctk.CTkLabel(left_frame, text="Your Input: ", font=self.set_font("Quicksand", 20, "bold"))
        self.lbl_typed.pack(pady=30)

        # ข้อมูลเกม
        ctk.CTkLabel(right_frame, text="Game Stats", font=self.set_font("Quicksand", 30, "bold")).pack(pady=20, padx=60)
        self.lbl_result = ctk.CTkLabel(right_frame, text="Prediction: ", font=self.set_font("Quicksand", 20, "bold"))
        self.lbl_result.pack(pady=10)
        self.lbl_time = ctk.CTkLabel(right_frame, text="Time: ", font=self.set_font("Quicksand", 20, "bold"))
        self.lbl_time.pack(pady=10)
        self.lbl_score = ctk.CTkLabel(right_frame, text="Score: ", font=self.set_font("Quicksand", 20, "bold"))
        self.lbl_score.pack(pady=10)

        # ปุ่มออก
        self.btn_exit = ctk.CTkButton(right_frame, text="❌ Exit", command=self.show_welcome_screen, fg_color="#f44336",
                                       font=self.set_font("Quicksand", 20, "bold"), width=180, height=70, corner_radius=25)
        self.btn_exit.pack(pady=20)


    def show_tutorial_screen(self):
        self.clear_screen()

        # หน้าจอ
        content_frame = ctk.CTkFrame(self.main_frame, corner_radius=20)
        content_frame.pack(expand=True)

        # หัวข้อ
        title_label = ctk.CTkLabel(content_frame, text="🎯 Tutorial", font=self.custom_font)
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # กล้อง
        self.video_frame = ctk.CTkLabel(content_frame, text="", corner_radius=20, width=580, height=480)
        self.video_frame.grid(row=1, column=0, padx=0, pady=0)

        # วีดีโอตัวอย่าง
        self.video_frame2 = ctk.CTkLabel(content_frame, text="",  corner_radius=20, width=580, height=480)
        self.video_frame2.grid(row=1, column=1, padx=0, pady=0)

        # --- Add these lines to show the white frame initially ---
        self.show_white_frame_in_view()

        # กล่องเลือกตัวอักษร
        self.letter_combo = ttk.Combobox(content_frame, values=[chr(i) for i in range(65, 91)], width=15, style='Custom.TCombobox',
                                         textvariable=tk.StringVar(), font=self.combobox_font, state='readonly')
        self.letter_combo.set("Select a Letter")
        self.letter_combo.grid(row=2, column=0, columnspan=2, pady=10)
        self.letter_combo.bind("<<ComboboxSelected>>", self.on_letter_selected)

        # --- Further Combobox adjustments (after creation)---
        self.letter_combo.option_add('*TCombobox*Listbox.font', self.combobox_font)
        self.letter_combo.option_add("*TCombobox*Listbox.selectBackground", "gray")
        self.letter_combo.option_add("*TCombobox*Listbox.selectForeground", "white")

        # ปุ่มออก
        back_button = ctk.CTkButton(content_frame, text="❌ Exit", command=self.show_welcome_screen, fg_color="#f44336",
                                    font=self.set_font("Quicksand", 20, "bold"), width=180, height=70, corner_radius=25)
        back_button.grid(row=3, column=0, columnspan=2, pady=20)

        self.controller.start_video_capture_tutorial()


    def show_white_frame_in_view(self):
        """Displays a white frame within the view."""
        white_frame = Image.new('RGB', (500, 375), 'white')
        rounded_white_frame = self._round_image(white_frame, (500, 375))
        imgtk = CTkImage(light_image=rounded_white_frame, dark_image=rounded_white_frame, size=(500, 375))
        self.video_frame2.configure(image=imgtk)
        self.video_frame2.imgtk = imgtk

    def on_letter_selected(self, event):
        selected_letter = self.letter_combo.get()
        print(f"Selected letter: {selected_letter}")
        self.controller.start_video_example(selected_letter)


    def clear_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()


    def _round_cam(self, frame, size, radius=50):
        """Rounds the corners of a camera frame."""
        if not isinstance(frame, Image.Image):
            img = Image.fromarray(frame)
        else:
            img = frame
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), img.size], radius, fill=255)
        img.putalpha(mask)
        img = img.resize(size)  # Resize after applying mask
        return img
    
    def _round_image(self, image, size, radius=15):
        """Rounds corners of general images/video frames (NOT camera)."""
        # Check if 'image' is a PIL Image; if not, convert.
        if not isinstance(image, Image.Image):
            img = Image.fromarray(image)
        else:
            img = image
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), img.size], radius, fill=255)
        img.putalpha(mask)
        img = img.resize(size)
        return img


    def update_tutorial_frame(self, frame, confirmed_prediction):
        img = self._round_cam(frame, (500, 375))  # Use the rounding function
        img_ctk = CTkImage(light_image=img, dark_image=img, size=(500, 375)) #size are not necessary
        self.video_frame.configure(image=img_ctk)
        self.video_frame.imgtk = img_ctk

        current_value = self.letter_combo.get()
        if current_value == "Select a Letter" and confirmed_prediction is not None:
            values = [chr(i) for i in range(65, 91)]
            if confirmed_prediction is not None:
                confirmed_letter = str(confirmed_prediction)
                if confirmed_letter in values:
                    current_index = values.index(confirmed_letter)
                    next_index = (current_index + 1) % len(values)
                    self.letter_combo.set(values[next_index])
                    self.on_letter_selected(None)
        if confirmed_prediction is not None and str(confirmed_prediction) == current_value:
            values = [chr(i) for i in range(65, 91)]
            if current_value in values:
                current_index = values.index(current_value)
                next_index = (current_index + 1) % len(values)
                self.letter_combo.set(values[next_index])
                self.on_letter_selected(None)

    def update_viedo_example(self, frame):
        img = self._round_image(frame, (500, 375))  # Round and resize
        img_ctk = CTkImage(light_image=img, dark_image=img, size=(500,375))
        self.video_frame2.configure(image=img_ctk)
        self.video_frame2.imgtk = img_ctk



    def update_frame(self, frame):
        """Updates the video frame with rounded corners."""
        # Convert frame to PIL Image
        img = Image.fromarray(frame)

        # --- Rounded Corner Logic ---
        radius = 20  # Adjust for desired corner roundness
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)

        # Draw rounded rectangle
        draw.rounded_rectangle([(0, 0), img.size], radius, fill=255)

        # Use the mask to make corners transparent
        img.putalpha(mask)

        # Convert back to CTkImage and update label
        img_ctk = CTkImage(light_image=img, dark_image=img, size=(640, 480))
        self.lbl_video.configure(image=img_ctk)
        self.lbl_video.imgtk = img_ctk  # Keep a reference!


    def update_labels(self, game_state, prediction_text):
        current_word = game_state["current_word"]
        typed_word = game_state["typed_word"]

        typed_part = typed_word
        remaining_part = current_word[len(typed_word):]

        self.lbl_word.config(state="normal")
        self.lbl_word.delete("1.0", "end")

        word_prefix = "📌 Word: "
        self.lbl_word.insert("1.0", word_prefix)
        self.lbl_word.tag_add("word_label", "1.0", f"1.{len(word_prefix)}")

        start_index = f"1.{len(word_prefix)}"
        self.lbl_word.insert(start_index, typed_part)
        self.lbl_word.tag_add("typed", start_index, f"1.{len(word_prefix) + len(typed_part)}")

        start_remaining = f"1.{len(word_prefix) + len(typed_part)}"
        self.lbl_word.insert(start_remaining, remaining_part)
        self.lbl_word.tag_add("remaining", start_remaining, "end")

        self.lbl_word.config(
            bg=self.root.cget("bg"),
            borderwidth=0,
            highlightthickness=0,
            state="disabled"
        )

        self.lbl_word.tag_configure("word_label", foreground="white")
        self.lbl_word.tag_configure("typed", foreground="green")
        self.lbl_word.tag_configure("remaining", foreground="white")

        self.lbl_typed.configure(text=f"📝 Your Input: {typed_word}")
        self.lbl_time.configure(text=f"⏳ Time: {game_state['remaining_time']:.2f} sec")
        self.lbl_score.configure(text=f"🏆 Score: {game_state['score']}")
        self.lbl_result.configure(text=f"🔍 {prediction_text}")

        if typed_word == current_word:
            def show_full_green():
                self.lbl_word.config(state="normal")
                self.lbl_word.tag_add("typed", "1.0", "end")
                self.lbl_word.config(state="disabled")
                self.lbl_typed.configure(text=f"📝 Your Input: {typed_word}")
                self.root.after(1000, self.controller.next_word)

            self.root.after(100, show_full_green)

    def start(self):
        self.root.mainloop()