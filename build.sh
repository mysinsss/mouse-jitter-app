#!/bin/bash
# Build script for creating standalone executable

echo "Building Mouse Jitter App executable..."
python -m PyInstaller --onefile --windowed --name MouseJitter mouse_jitter.py

echo "Build complete! Executable located in: dist/MouseJitter.exe"
echo "You can now distribute this executable without requiring Python or dependencies."