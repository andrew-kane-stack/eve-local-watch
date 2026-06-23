"""
build.py — builds EVE Local Watch.exe
Run: python build.py
Requirements: pip install pyinstaller  +  pip install -r requirements.txt
"""
import subprocess, sys, os

try:
    import PyInstaller
except ImportError:
    print("Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

here      = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(here, "icon.ico")
exe_path  = os.path.join(here, "dist", "EVE Local Watch.exe")

if not os.path.exists(icon_path):
    print("ERROR: icon.ico not found — put it in the same folder as this script.")
    sys.exit(1)

args = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--windowed",
    "--name", "EVE Local Watch",
    "--icon", icon_path,
    # Ensure icon is also bundled as a data file so runtime iconphoto() works
    f"--add-data={icon_path};.",
    "--hidden-import", "plyer.platforms.win.notification",
    "--hidden-import", "sounddevice",
    "--hidden-import", "mss.windows",
    "--hidden-import", "pyautogui",
    "--hidden-import", "PIL._tkinter_finder",
    "--hidden-import", "PIL.IcoImagePlugin",
    os.path.join(here, "eve_local_watch.py"),
]

print("Building EVE Local Watch.exe …")
result = subprocess.run(args, cwd=here)

if result.returncode != 0:
    print("\n❌  Build failed.")
    sys.exit(1)

print(f"\n✅  Build successful!")
if os.path.exists(exe_path):
    size_mb = os.path.getsize(exe_path) / 1024 / 1024
    print(f"    {exe_path}  ({size_mb:.1f} MB)")
print(f"\n    Share just this one .exe — nothing else needed.")
print(f"    config.json is created next to the .exe on first run.")
