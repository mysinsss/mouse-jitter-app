import sys
import threading
import math
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QPushButton, QComboBox, QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QTimer, QPoint
from PyQt6.QtGui import QFont, QIcon
from pynput import keyboard
import pyautogui
import json
import os

# Disable pyautogui safety features
pyautogui.FAILSAFE = False


class GlobalHotKeyListener(QObject):
    """Listen for global hotkey presses"""
    hotkey_pressed = pyqtSignal()
    
    def __init__(self, key_combo):
        super().__init__()
        self.key_combo = key_combo
        self.listener = None
        self.start_listening()
    
    def start_listening(self):
        """Start listening for hotkey"""
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
    
    def on_press(self, key):
        """Handle key press"""
        try:
            if hasattr(key, 'char'):
                if key.char and key.char.lower() == self.key_combo.lower():
                    self.hotkey_pressed.emit()
            elif hasattr(key, 'name'):
                if key.name == self.key_combo:
                    self.hotkey_pressed.emit()
        except AttributeError:
            pass
    
    def stop_listening(self):
        """Stop listening"""
        if self.listener:
            self.listener.stop()
    
    def change_key(self, new_key):
        """Change the hotkey"""
        self.key_combo = new_key


class JitterController(QObject):
    """Handles mouse jitter logic with Apex-style aim patterns"""
    
    def __init__(self):
        super().__init__()
        self.is_running = False
        self.jitter_intensity = 15
        self.jitter_speed = 50
        self.pattern_type = "circular"
        self.angle = 0
        self.sensitivity_mult = 1.0
        self.start_time = None
        
    def start_jitter(self):
        """Start the jitter thread"""
        if not self.is_running:
            self.is_running = True
            self.start_time = time.time()
            thread = threading.Thread(target=self._jitter_loop, daemon=True)
            thread.start()
    
    def stop_jitter(self):
        """Stop the jitter"""
        self.is_running = False
    
    def get_active_time(self):
        """Get how long jitter has been active"""
        if self.start_time and self.is_running:
            return int(time.time() - self.start_time)
        return 0
    
    def _jitter_loop(self):
        """Main jitter loop with Apex-style patterns"""
        while self.is_running:
            try:
                current_x, current_y = pyautogui.position()
                
                if self.pattern_type == "circular":
                    jitter_x, jitter_y = self._circular_pattern()
                elif self.pattern_type == "figure8":
                    jitter_x, jitter_y = self._figure8_pattern()
                elif self.pattern_type == "spiral":
                    jitter_x, jitter_y = self._spiral_pattern()
                elif self.pattern_type == "zigzag":
                    jitter_x, jitter_y = self._zigzag_pattern()
                elif self.pattern_type == "wave":
                    jitter_x, jitter_y = self._wave_pattern()
                else:
                    jitter_x, jitter_y = self._circular_pattern()
                
                # Apply sensitivity multiplier
                jitter_x = int(jitter_x * self.sensitivity_mult)
                jitter_y = int(jitter_y * self.sensitivity_mult)
                
                new_x = current_x + jitter_x
                new_y = current_y + jitter_y
                
                pyautogui.moveTo(new_x, new_y, duration=0.0005)
                
                self.angle += (100 - self.jitter_speed) / 8
                if self.angle >= 360:
                    self.angle = 0
                
                sleep_time = (100 - self.jitter_speed) / 2500
                threading.Event().wait(sleep_time)
                
            except Exception as e:
                print(f"Error in jitter loop: {e}")
                self.is_running = False
    
    def _circular_pattern(self):
        """Circular jitter pattern - smooth circle movement"""
        radius = self.jitter_intensity * 1.2
        angle_rad = math.radians(self.angle)
        
        jitter_x = int(radius * math.cos(angle_rad))
        jitter_y = int(radius * math.sin(angle_rad))
        
        return jitter_x, jitter_y
    
    def _figure8_pattern(self):
        """Figure-8 pattern - pro player micro-adjust"""
        t = math.radians(self.angle)
        a = self.jitter_intensity * 0.8
        
        denominator = 1 + math.sin(t) ** 2
        jitter_x = int((a * math.cos(t)) / denominator * 1.5)
        jitter_y = int((a * math.sin(t) * math.cos(t)) / denominator * 1.5)
        
        return jitter_x, jitter_y
    
    def _spiral_pattern(self):
        """Spiral pattern - expanding/contracting"""
        angle_rad = math.radians(self.angle)
        
        spiral_factor = (math.sin(self.angle / 180) + 1) / 2
        radius = self.jitter_intensity * spiral_factor * 1.3
        
        jitter_x = int(radius * math.cos(angle_rad))
        jitter_y = int(radius * math.sin(angle_rad))
        
        return jitter_x, jitter_y
    
    def _zigzag_pattern(self):
        """Zigzag pattern - aggressive left-right"""
        zigzag_x = int(self.jitter_intensity * 1.4 * math.sin(math.radians(self.angle)))
        zigzag_y = int(self.jitter_intensity * 0.5 * math.cos(math.radians(self.angle * 2)))
        
        return zigzag_x, zigzag_y
    
    def _wave_pattern(self):
        """Wave pattern - up-down recoil control"""
        wave_y = int(self.jitter_intensity * 1.4 * math.sin(math.radians(self.angle)))
        wave_x = int(self.jitter_intensity * 0.5 * math.cos(math.radians(self.angle * 2)))
        
        return wave_x, wave_y


class MouseJitterApp(QMainWindow):
    """Main application window with gaming aesthetic"""
    
    PROFILES = {
        "Rifle": {"intensity": 18, "speed": 55, "pattern": "Figure-8", "sensitivity": 1.1},
        "SMG": {"intensity": 22, "speed": 65, "pattern": "Zigzag", "sensitivity": 1.2},
        "Pistol": {"intensity": 12, "speed": 45, "pattern": "Circular", "sensitivity": 0.9},
        "Shotgun": {"intensity": 15, "speed": 50, "pattern": "Wave", "sensitivity": 1.0},
        "Sniper": {"intensity": 8, "speed": 40, "pattern": "Circular", "sensitivity": 0.8},
    }
    
    def __init__(self):
        super().__init__()
        self.controller = JitterController()
        self.hotkey_listener = None
        self.active_hotkey = "x"
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.load_settings()
        self.init_ui()
        self.setup_hotkey()
        
    def init_ui(self):
        """Initialize the user interface with gaming theme"""
        self.setWindowTitle("APEX JITTER PRO - Advanced Edition")
        self.setGeometry(100, 100, 800, 750)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        # Dark gaming theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0e27;
            }
            QWidget {
                background-color: #0a0e27;
                color: #00d9ff;
            }
            QLabel {
                color: #00d9ff;
            }
            QComboBox {
                background-color: #1a1f3a;
                color: #00d9ff;
                border: 2px solid #00d9ff;
                padding: 5px;
                font-weight: bold;
            }
            QSlider::groove:horizontal {
                background-color: #1a1f3a;
                height: 8px;
                border: 1px solid #00d9ff;
            }
            QSlider::handle:horizontal {
                background-color: #00ff41;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QPushButton {
                border: 2px solid #00d9ff;
                border-radius: 8px;
                font-weight: bold;
                padding: 8px;
                background-color: #1a1f3a;
            }
            QPushButton:hover {
                background-color: #00d9ff;
                color: #0a0e27;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("⚡ APEX JITTER PRO ⚡")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #00ff41; text-align: center; padding: 10px;")
        main_layout.addWidget(title)
        
        # Quick Presets Row
        presets_label = QLabel("🎯 QUICK PRESETS")
        presets_label.setStyleSheet("color: #ff006e; font-weight: bold; font-size: 11pt;")
        main_layout.addWidget(presets_label)
        
        presets_layout = QHBoxLayout()
        for preset_name in self.PROFILES.keys():
            preset_btn = QPushButton(preset_name)
            preset_btn.setMaximumWidth(120)
            preset_btn.clicked.connect(lambda checked, name=preset_name: self.apply_preset(name))
            presets_layout.addWidget(preset_btn)
        main_layout.addLayout(presets_layout)
        
        # Hotkey Section
        hotkey_label = QLabel("🎮 HOTKEY SETTINGS")
        hotkey_label.setStyleSheet("color: #ff006e; font-weight: bold; font-size: 11pt; padding-top: 10px;")
        main_layout.addWidget(hotkey_label)
        
        hotkey_layout = QHBoxLayout()
        key_label = QLabel("Activation Key:")
        key_label.setMinimumWidth(100)
        key_label.setStyleSheet("color: #00d9ff; font-weight: bold;")
        hotkey_layout.addWidget(key_label)
        
        self.hotkey_combo = QComboBox()
        self.hotkey_combo.addItems(["x", "z", "c", "v", "space", "shift", "ctrl", "alt"])
        self.hotkey_combo.setCurrentText(self.active_hotkey)
        self.hotkey_combo.currentTextChanged.connect(self.change_hotkey)
        hotkey_layout.addWidget(self.hotkey_combo)
        
        self.hotkey_status = QLabel("✓ Ready")
        self.hotkey_status.setStyleSheet("color: #00ff41; font-weight: bold;")
        hotkey_layout.addWidget(self.hotkey_status)
        
        main_layout.addLayout(hotkey_layout)
        
        # Pattern Selection
        pattern_label = QLabel("🎯 PATTERN SELECTION")
        pattern_label.setStyleSheet("color: #ff006e; font-weight: bold; font-size: 11pt; padding-top: 10px;")
        main_layout.addWidget(pattern_label)
        
        pattern_layout = QHBoxLayout()
        pat_label = QLabel("Pattern:")
        pat_label.setMinimumWidth(100)
        pat_label.setStyleSheet("color: #00d9ff; font-weight: bold;")
        pattern_layout.addWidget(pat_label)
        
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems(["Circular", "Figure-8", "Spiral", "Zigzag", "Wave"])
        self.pattern_combo.currentTextChanged.connect(self.update_pattern)
        pattern_layout.addWidget(self.pattern_combo)
        
        main_layout.addLayout(pattern_layout)
        
        # Intensity
        intensity_label = QLabel("⚙️ INTENSITY & SPEED")
        intensity_label.setStyleSheet("color: #ff006e; font-weight: bold; font-size: 11pt; padding-top: 10px;")
        main_layout.addWidget(intensity_label)
        
        intensity_layout = QHBoxLayout()
        int_label = QLabel("Intensity:")
        int_label.setMinimumWidth(100)
        int_label.setStyleSheet("color: #00d9ff; font-weight: bold;")
        intensity_layout.addWidget(int_label)
        
        self.intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.intensity_slider.setMinimum(1)
        self.intensity_slider.setMaximum(60)
        self.intensity_slider.setValue(15)
        self.intensity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.intensity_slider.setTickInterval(5)
        self.intensity_slider.valueChanged.connect(self.update_intensity)
        intensity_layout.addWidget(self.intensity_slider)
        
        self.intensity_value = QLabel("15")
        self.intensity_value.setMinimumWidth(50)
        self.intensity_value.setStyleSheet("color: #00ff41; font-weight: bold; font-size: 11pt;")
        intensity_layout.addWidget(self.intensity_value)
        
        main_layout.addLayout(intensity_layout)
        
        # Speed
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Speed:")
        speed_label.setMinimumWidth(100)
        speed_label.setStyleSheet("color: #00d9ff; font-weight: bold;")
        speed_layout.addWidget(speed_label)
        
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(50)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(10)
        self.speed_slider.valueChanged.connect(self.update_speed)
        speed_layout.addWidget(self.speed_slider)
        
        self.speed_value = QLabel("50")
        self.speed_value.setMinimumWidth(50)
        self.speed_value.setStyleSheet("color: #00ff41; font-weight: bold; font-size: 11pt;")
        speed_layout.addWidget(self.speed_value)
        
        main_layout.addLayout(speed_layout)
        
        # Sensitivity Multiplier
        sensitivity_layout = QHBoxLayout()
        sens_label = QLabel("Sensitivity:")
        sens_label.setMinimumWidth(100)
        sens_label.setStyleSheet("color: #00d9ff; font-weight: bold;")
        sensitivity_layout.addWidget(sens_label)
        
        self.sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity_slider.setMinimum(50)
        self.sensitivity_slider.setMaximum(150)
        self.sensitivity_slider.setValue(100)
        self.sensitivity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.sensitivity_slider.setTickInterval(10)
        self.sensitivity_slider.valueChanged.connect(self.update_sensitivity)
        sensitivity_layout.addWidget(self.sensitivity_slider)
        
        self.sensitivity_value = QLabel("1.0x")
        self.sensitivity_value.setMinimumWidth(50)
        self.sensitivity_value.setStyleSheet("color: #00ff41; font-weight: bold; font-size: 11pt;")
        sensitivity_layout.addWidget(self.sensitivity_value)
        
        main_layout.addLayout(sensitivity_layout)
        
        # Status & Stats
        self.status_label = QLabel("Status: INACTIVE")
        status_font = QFont()
        status_font.setPointSize(13)
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        self.status_label.setStyleSheet("color: #ff006e; padding: 12px; text-align: center;")
        main_layout.addWidget(self.status_label)
        
        self.stats_label = QLabel("Active Time: 0s")
        self.stats_label.setStyleSheet("color: #00d9ff; text-align: center; font-size: 10pt;")
        main_layout.addWidget(self.stats_label)
        
        # Control Buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("▶ START")
        self.start_button.clicked.connect(self.start_jitter)
        self.start_button.setMinimumHeight(45)
        self.start_button.setStyleSheet("background-color: #00ff41; color: #0a0e27; border: 2px solid #00ff41;")
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("⏹ STOP")
        self.stop_button.clicked.connect(self.stop_jitter)
        self.stop_button.setMinimumHeight(45)
        self.stop_button.setStyleSheet("background-color: #ff006e; color: #fff;")
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        reset_button = QPushButton("⟲ RESET")
        reset_button.clicked.connect(self.reset_settings)
        reset_button.setMinimumHeight(45)
        reset_button.setStyleSheet("background-color: #ffaa00; color: #0a0e27; border: 2px solid #ffaa00;")
        button_layout.addWidget(reset_button)
        
        main_layout.addLayout(button_layout)
        
        # Safety Info
        safety_label = QLabel("⚠️  Press bound key to toggle | Always-on-top enabled")
        safety_font = QFont()
        safety_font.setPointSize(9)
        safety_label.setFont(safety_font)
        safety_label.setStyleSheet("color: #ffaa00; text-align: center; padding: 8px;")
        main_layout.addWidget(safety_label)
        
        main_layout.addStretch()
        central_widget.setLayout(main_layout)
    
    def apply_preset(self, preset_name):
        """Apply a preset configuration"""
        if preset_name in self.PROFILES:
            preset = self.PROFILES[preset_name]
            self.intensity_slider.setValue(preset["intensity"])
            self.speed_slider.setValue(preset["speed"])
            self.pattern_combo.setCurrentText(preset["pattern"])
            sens_value = int(preset["sensitivity"] * 100)
            self.sensitivity_slider.setValue(sens_value)
            self.save_settings()
    
    def setup_hotkey(self):
        """Setup global hotkey listener"""
        self.hotkey_listener = GlobalHotKeyListener(self.active_hotkey)
        self.hotkey_listener.hotkey_pressed.connect(self.toggle_jitter)
    
    def toggle_jitter(self):
        """Toggle jitter on/off with hotkey"""
        if self.controller.is_running:
            self.stop_jitter()
        else:
            self.start_jitter()
    
    def change_hotkey(self, new_key):
        """Change the hotkey binding"""
        self.active_hotkey = new_key
        if self.hotkey_listener:
            self.hotkey_listener.stop_listening()
        self.setup_hotkey()
        self.hotkey_status.setText(f"✓ '{new_key.upper()}'")
        self.save_settings()
    
    def update_pattern(self, pattern_name):
        """Update jitter pattern type"""
        pattern_map = {
            "Circular": "circular",
            "Figure-8": "figure8",
            "Spiral": "spiral",
            "Zigzag": "zigzag",
            "Wave": "wave"
        }
        self.controller.pattern_type = pattern_map.get(pattern_name, "circular")
        self.controller.angle = 0
        self.save_settings()
    
    def update_intensity(self, value):
        """Update jitter intensity"""
        self.controller.jitter_intensity = value
        self.intensity_value.setText(str(value))
        self.save_settings()
    
    def update_speed(self, value):
        """Update jitter speed"""
        self.controller.jitter_speed = value
        self.speed_value.setText(str(value))
        self.save_settings()
    
    def update_sensitivity(self, value):
        """Update sensitivity multiplier"""
        self.controller.sensitivity_mult = value / 100.0
        self.sensitivity_value.setText(f"{value/100:.1f}x")
        self.save_settings()
    
    def update_stats(self):
        """Update active time display"""
        if self.controller.is_running:
            active_time = self.controller.get_active_time()
            self.stats_label.setText(f"Active Time: {active_time}s")
    
    def start_jitter(self):
        """Start jitter"""
        self.controller.start_jitter()
        self.status_label.setText("Status: ACTIVE ⚡")
        self.status_label.setStyleSheet("color: #00ff41; padding: 12px; text-align: center; font-weight: bold;")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.pattern_combo.setEnabled(False)
        self.timer.start(100)
    
    def stop_jitter(self):
        """Stop jitter"""
        self.controller.stop_jitter()
        self.status_label.setText("Status: INACTIVE")
        self.status_label.setStyleSheet("color: #ff006e; padding: 12px; text-align: center; font-weight: bold;")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.pattern_combo.setEnabled(True)
        self.timer.stop()
        self.stats_label.setText("Active Time: 0s")
        self.save_settings()
    
    def reset_settings(self):
        """Reset all settings to default"""
        self.intensity_slider.setValue(15)
        self.speed_slider.setValue(50)
        self.sensitivity_slider.setValue(100)
        self.pattern_combo.setCurrentText("Circular")
        self.hotkey_combo.setCurrentText("x")
        if self.controller.is_running:
            self.stop_jitter()
        self.save_settings()
    
    def save_settings(self):
        """Save settings to file"""
        settings = {
            "intensity": self.controller.jitter_intensity,
            "speed": self.controller.jitter_speed,
            "pattern": self.pattern_combo.currentText(),
            "sensitivity": self.controller.sensitivity_mult,
            "hotkey": self.active_hotkey
        }
        try:
            with open("jitter_settings.json", "w") as f:
                json.dump(settings, f)
        except:
            pass
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists("jitter_settings.json"):
                with open("jitter_settings.json", "r") as f:
                    settings = json.load(f)
                    self.controller.jitter_intensity = settings.get("intensity", 15)
                    self.controller.jitter_speed = settings.get("speed", 50)
                    self.controller.sensitivity_mult = settings.get("sensitivity", 1.0)
                    self.active_hotkey = settings.get("hotkey", "x")
        except:
            pass
    
    def closeEvent(self, event):
        """Cleanup when closing"""
        if self.hotkey_listener:
            self.hotkey_listener.stop_listening()
        if self.controller.is_running:
            self.controller.stop_jitter()
        self.save_settings()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MouseJitterApp()
    window.show()
    sys.exit(app.exec())
