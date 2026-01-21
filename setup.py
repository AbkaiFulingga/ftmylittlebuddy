import cx_Freeze
import sys

# Determine the base based on the platform
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Use this to avoid console window on Windows

# Include all necessary files and modules
executables = [cx_Freeze.Executable(
    "main.py",
    base=base,
    target_name="MyLittleBuddy.exe",  # Name of the executable
    icon=None  # Add path to an icon file if you have one (e.g., "icon.ico")
)]

# Build options
build_exe_options = {
    "packages": ["tkinter", "threading", "time", "json", "os", "random"],
    "excludes": [],
    "include_files": [
        "assets.py",
        "game_state.py",
        "mini_games.py",
        "pets.py"
    ],  # Include all necessary game files
    "optimize": 2,
    "include_msvcrt": True  # Include Microsoft Visual C++ Runtime for Windows compatibility
}

cx_Freeze.setup(
    name="MyLittleBuddy",
    version="1.0",
    description="A charming virtual pet simulator inspired by Moshi Monsters, Tamagotchi, and Neopets",
    options={"build_exe": build_exe_options},
    executables=executables
)
