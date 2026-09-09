# Mouse Jitter App

A simple desktop application to create controlled mouse jitter with adjustable intensity and speed settings.

## Features

- **Jitter Intensity Slider**: Control the range of mouse movement (1-50 pixels)
- **Jitter Speed Slider**: Control how fast the jitter occurs (1-100)
- **Start/Stop Controls**: Easy toggle buttons to enable/disable jitter
- **Real-time Status**: Shows whether jitter is active or stopped
- **Emergency Stop**: Move your mouse to the top-left corner of the screen to forcefully stop

## Quick Start (Standalone Executable)

### Windows:
1. Download the files from this repository
2. Open Command Prompt in the folder
3. Run: `build.bat`
4. Wait for the build to complete
5. Open the `dist` folder
6. Double-click `MouseJitter.exe` to run
7. No Python installation needed after this!

### Mac/Linux:
1. Download the files from this repository
2. Open Terminal in the folder
3. Run: `bash build.sh`
4. Wait for the build to complete
5. Open the `dist` folder
6. Run `./MouseJitter` to start the app

## Installation (For Developers)

If you want to run from source:

1. Clone the repository:
```bash
git clone https://github.com/mysinsss/mouse-jitter-app.git
cd mouse-jitter-app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python mouse_jitter.py
```

## Settings

- **Jitter Intensity Range**: 1-50 pixels
- **Jitter Speed Range**: 1-100 (100 = fastest)

## Safety

⚠️ Always keep your mouse movement available for emergency stops. The app includes a fail-safe where moving to the top-left corner will stop jitter.

## Requirements (for source installation)

- Python 3.7+
- PyQt6
- pyautogui

## License

MIT