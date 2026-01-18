#!/bin/bash
# Build script for My Little Buddy

echo "Building My Little Buddy executables..."

# Create dist directory if it doesn't exist
mkdir -p dist

# Build the executable using PyInstaller
echo "Creating executable..."
source .venv/bin/activate && pyinstaller MyLittleBuddy.spec
echo "Build complete! Executable is located in the 'dist' folder."
echo "You can find the executable at: dist/MyLittleBuddy"
