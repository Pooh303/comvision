# main.py
from controller import SignLanguageController
from install_font import install_fonts_from_folder
from PIL import ImageFont

def is_font_installed(font_name):
    try:
        ImageFont.truetype(font_name, 12)
        return True
    except IOError:
        return False

if not is_font_installed("Quicksand.ttf"):
    install_fonts_from_folder('assets/fonts/Quicksand')

if __name__ == "__main__":
    controller = SignLanguageController()
    controller.run()