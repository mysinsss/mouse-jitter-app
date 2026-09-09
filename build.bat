@echo off
REM Build script for Windows
echo Building Mouse Jitter App executable...
python -m PyInstaller --onefile --windowed --name MouseJitter mouse_jitter.py

echo.
echo Build complete! Your executable is in the dist folder.
echo You can now run MouseJitter.exe without needing Python!
pause