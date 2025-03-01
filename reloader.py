import time
import subprocess
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TkinterAppReloader(FileSystemEventHandler):
    def __init__(self, app_file):
        super().__init__()
        self.app_file = app_file
        self.process = None
        self.start_app()

    def start_app(self):
        if self.process:
            print("Stopping previous process...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)  # รอให้ process เก่าปิดสนิท (5 วินาที)
            except subprocess.TimeoutExpired:
                print("Force killing process...")
                self.process.kill() # หาก terminate() ไม่สำเร็จ ให้ kill()
                self.process.wait()

        print(f"Starting {self.app_file}...")
        self.process = subprocess.Popen([sys.executable, self.app_file])

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"Detected change in {event.src_path}, restarting...")
            self.start_app()

if __name__ == "__main__":
    app_file = "main.py"  #  ระบุไฟล์ entry point ของแอปคุณ (ไฟล์ที่รันแล้วเปิดแอป)
    event_handler = TkinterAppReloader(app_file)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)  # ตรวจสอบทั้ง directory ปัจจุบัน
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process: # ปิด process ของแอปก่อนจบการทำงาน
            event_handler.process.terminate()
            event_handler.process.wait()
    observer.join()