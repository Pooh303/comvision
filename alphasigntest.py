import customtkinter as ctk
import threading
import inference_classifier

def show_main_menu():
    """แสดงหน้าเมนูหลัก"""
    clear_window()
    
    label = ctk.CTkLabel(root, text="🎮 Welcome to Alpha Signing!", font=("Arial", 24))
    label.pack(pady=20)

    start_button = ctk.CTkButton(root, text="เริ่มเกม", command=start_game)
    start_button.pack(pady=10)

    howto_button = ctk.CTkButton(root, text="วิธีเล่น", command=show_how_to_play)
    howto_button.pack(pady=10)

    quit_button = ctk.CTkButton(root, text="ออก", command=root.quit)
    quit_button.pack(pady=10)

def start_game():
    """เริ่มเกม (ยังไม่เชื่อมต่อ)"""
    play_game = threading.Thread(target=inference_classifier.run_game())
    play_game.start()

def show_how_to_play():
    """แสดงหน้าวิธีเล่น"""
    clear_window()
    
    label = ctk.CTkLabel(root, text="📖 วิธีเล่นเกม\n\n1️. ใช้กล้องในการอ่านภาษามือ\n2️. ทำสัญลักษณ์ให้ตรงกับตัวอักษรที่กำหนด\n3️. พิมพ์คำให้ครบเพื่อชนะ!", font=("Arial", 20))
    label.pack(pady=20)

    back_button = ctk.CTkButton(root, text="⬅️ กลับไปหน้าหลัก", command=show_main_menu)
    back_button.pack(pady=20)


def clear_window():
    """ล้างหน้าจอทั้งหมด"""
    for widget in root.winfo_children():
        widget.destroy()

# ตั้งค่า customtkinter
root = ctk.CTk()
root.title("Alpha Signing Game")
root.geometry("800x600")

# โหลดหน้าแรก
show_main_menu()

root.mainloop()
