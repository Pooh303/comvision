# main.py
from controller import SignLanguageController

# font.install_fonts_from_folder("assets/fonts/Quicksand")

if __name__ == "__main__":
    controller = SignLanguageController()
    controller.run()