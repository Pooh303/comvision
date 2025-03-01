import tkinter as tk
import tkinter.font as tkfont
import customtkinter as ctk
from customtkinter import CTkImage
from tkinter import ttk
from PIL import Image, ImageTk

# Hiding warnings
import warnings
warnings.filterwarnings("ignore")

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

        # --- Load the custom font (using CTkFont) for most widgets---
        try:
            self.custom_font = ctk.CTkFont(family="Quicksand", size=40, weight="bold")
        except tk.TclError:
            print("Error: Could not load custom font 'Quicksand'.")
            print("Falling back to Arial.")
            self.custom_font = ctk.CTkFont(family="Arial", size=40, weight="bold")

        # --- Create a separate tkinter.font.Font for the Combobox ---
        try:
            self.combobox_font = tkfont.Font(family="Quicksand", size=24, weight="bold") # Use tkfont.Font
            self.combobox_font.actual() # Check if font loaded
        except tk.TclError:
            print("Error: Could not load font for Combobox.  Falling back to Arial.")
            self.combobox_font = tkfont.Font(family="Arial", size=24, weight="bold")

         # --- Store base font settings ---
        self.base_font_family = "Quicksand"
        self.base_font_size = 40
        self.base_font_weight = "bold"

        # --- Create a separate tkinter.font.Font for the Combobox ---
        try:
            self.combobox_font = tkfont.Font(family=self.base_font_family, size=24, weight=self.base_font_weight)
            self.combobox_font.actual()  # Check if font loaded
        except tk.TclError:
            print("Error: Could not load font for Combobox.  Falling back to Arial.")
            self.combobox_font = tkfont.Font(family="Arial", size=24, weight="bold")

        self.combobox_font.configure(size=36)  # Modify the size AFTER creation

        self.show_welcome_screen()


    def set_font(self, family="Arial", size=20, weight="bold"):
        try:
            font = ctk.CTkFont(family=family, size=size, weight=weight)
            return font
        except tk.TclError:
            print(f"Error: Could not create font with family '{family}'. Falling back to Arial.")
            return ctk.CTkFont(family="Arial", size=size, weight=weight) #return CTkFont


    def show_tutorial_screen(self):
        self.clear_screen()
        content_frame = ctk.CTkFrame(self.main_frame)
        content_frame.pack(expand=True, fill="both", padx=10, pady=10)

        title_label = ctk.CTkLabel(content_frame, text="🎯 Tutorial", font=self.custom_font)
        title_label.grid(row=0, column=0, columnspan=2, pady=20)

        self.video_frame = ctk.CTkLabel(content_frame, text="", fg_color="black", corner_radius=10, width=500, height=375)
        self.video_frame.grid(row=1, column=0, padx=10, pady=20)
        self.video_frame2 = ctk.CTkLabel(content_frame, text="", fg_color="black", corner_radius=10, width=500, height=375)
        self.video_frame2.grid(row=1, column=1, padx=10, pady=20)

        # --- Use the separate tkinter.font.Font for the Combobox style ---
        self.letter_combo = ttk.Combobox(content_frame, values=[chr(i) for i in range(65, 91)], width=30)
        self.letter_combo.set("Select a Letter")
        self.letter_combo.grid(row=2, column=0, columnspan=2, pady=10)
        self.letter_combo.bind("<<ComboboxSelected>>", self.on_letter_selected)

        back_button = ctk.CTkButton(
            content_frame, text="⬅️Back", command=self.show_welcome_screen, font=self.set_font("Quicksand", 20, "bold"),
            fg_color="#ff5722", width=100, height=40, corner_radius=28
        )
        back_button.grid(row=3, column=0, columnspan=2, pady=20)
        self.controller.start_video_capture_tutorial()

    # --- (Rest of your class methods) ---
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
        btn_tutorial = ctk.CTkButton(welcome_frame, text="📖 Tutorial", command=self.show_tutorial_screen, font=self.set_font("Quicksand", 25, "bold"), fg_color="#2196f3", width=260, height=70, corner_radius=25)
        btn_tutorial.pack(pady=20)
        btn_exit = ctk.CTkButton(welcome_frame, text="❌ Exit", command=self.root.quit, font=self.set_font("Quicksand", 25, "bold"), fg_color="#f44336", width=260, height=70, corner_radius=25)
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

        right_frame = ctk.CTkFrame(game_frame, corner_radius=10)  # Removed width constraint
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10) # expand and fill both

        self.lbl_video = ctk.CTkLabel(left_frame, text="", fg_color="black", corner_radius=10, width=800, height=600)
        self.lbl_video.pack(fill="both", expand=True)

        self.lbl_word = tk.Text(left_frame, font=self.set_font("Quicksand", 30, "bold"), width=20, height=1, wrap="none", bg="black", fg="white", bd=0)
        self.lbl_word.pack(pady=10)
        self.lbl_word.tag_configure("typed", foreground="green")
        self.lbl_word.tag_configure("remaining", foreground="white")

        self.lbl_typed = ctk.CTkLabel(left_frame, text="Your Input: ", font=self.set_font("Quicksand", 20, "bold"))
        self.lbl_typed.pack(pady=10)

        ctk.CTkLabel(right_frame, text="Game Stats", font=self.set_font("Quicksand", 25, "bold")).pack(pady=20)
        self.lbl_result = ctk.CTkLabel(right_frame, text="Prediction: ", font=self.set_font("Quicksand", 20, "bold"))
        self.lbl_result.pack(pady=10)
        self.lbl_time = ctk.CTkLabel(right_frame, text="Time: ", font=self.set_font("Quicksand", 20, "bold"))
        self.lbl_time.pack(pady=10)
        self.lbl_score = ctk.CTkLabel(right_frame, text="Score: ", font=self.set_font("Quicksand", 20, "bold"))
        self.lbl_score.pack(pady=10)

        self.btn_exit = ctk.CTkButton(right_frame, text="❌ Exit", command=self.show_welcome_screen, fg_color="#f44336", font=self.set_font("Quicksand", 20, "bold"), width=180, height=70, corner_radius=25)
        self.btn_exit.pack(pady=20)

    def update_tutorial_frame(self, frame, confirmed_prediction):
        img = Image.fromarray(frame)
        img_ctk = CTkImage(light_image=img, dark_image=img, size=(500, 375))
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