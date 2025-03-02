import os
import shutil
import ctypes
import sys
import winreg  # Added for registry modification


def is_user_admin():
    """Check if the user has admin rights (Windows-specific)."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except AttributeError:
        return False  # Assume not admin if we can't check


def install_fonts_from_folder(folder_path):
    """Installs TrueType fonts from a specified folder."""

    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory.")
        return

    if not is_user_admin():
        # Request admin privileges and restart.  This is the crucial part.
        params = " ".join([f'"{arg}"' for arg in sys.argv[1:]]) # Pass all arguments!
        print("Requesting administrator privileges...")
        exit_code = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{sys.argv[0]}" {params}', None, 1
        )
        # Check if elevation was successful (exit_code > 32 indicates success).
        if exit_code <= 32:
            print("Administrator privileges are required to install fonts.")
            sys.exit(1)  # Exit with an error code
        else:
            sys.exit(0)  # Exit cleanly, the elevated process will continue


    # Get all .ttf files in the folder
    ttf_files = [f for f in os.listdir(folder_path) if f.endswith('.ttf')]
    if not ttf_files:
        print(f"No .ttf files found in '{folder_path}'.")
        return

    fonts_directory = os.path.join(os.environ['WINDIR'], 'Fonts')
    print(f"Installing fonts to: {fonts_directory}")

    for font_file in ttf_files:
        font_path = os.path.join(folder_path, font_file)
        destination_path = os.path.join(fonts_directory, font_file)
        try:
            shutil.copy(font_path, destination_path)
            print(f"Font {font_file} copied.")

            # Add font resource and update registry (for persistent install).
            if ctypes.windll.gdi32.AddFontResourceW(destination_path) == 0:
                print(f"Warning: AddFontResourceW failed for {font_file}")
            else:
              print(f"AddFontResourceW success for {font_file}")
                # Add to the registry (more reliable than just AddFontResource)
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts",
                    0,
                    winreg.KEY_WRITE,
                )
                # Get the font name (without the .ttf extension)
                font_name = os.path.splitext(font_file)[0]

                winreg.SetValueEx(key, f"{font_name} (TrueType)", 0, winreg.REG_SZ, font_file)
                winreg.CloseKey(key)
                print(f"Registry entry added for {font_file}.")

            except Exception as e:
              print(f"Failed to add registry {font_file}: {e}")


        except (shutil.Error, PermissionError) as e:
            print(f"Failed to install font {font_file}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while installing {font_file}: {e}")

    # Refresh font cache (SendMessageTimeoutW is more reliable than SendMessageW)
    HWND_BROADCAST = 0xFFFF
    WM_FONTCHANGE = 0x001D
    SMTO_ABORTIFHUNG = 0x0002

    result = ctypes.windll.user32.SendMessageTimeoutW(
        HWND_BROADCAST, WM_FONTCHANGE, 0, 0, SMTO_ABORTIFHUNG, 5000, None
    )
    if result == 0:
        print("Failed to refresh font cache.")
    else:
        print("Font cache refreshed.")
        