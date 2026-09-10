import sys
import threading
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QPushButton, QComboBox
)
from PyQt6.QtCore import Qt, QObject
from PyQt6.QtGui import QFont
import pyautogui

# Disable pyautogui safety features
pyautogui.FAILSAFE = False


class JitterController(QObject):
    """Handles mouse jitter logic with Apex-style aim patterns"""
    
    def __init__(self):
        super().__init__()
        self.is_running = False
        self.jitter_intensity = 5
        self.jitter_speed = 50
        self.pattern_type = "circular"
        self.angle = 0
        
    def start_jitter(self):
        """Start the jitter thread"""
        if not self.is_running:
            self.is_running = True
            thread = threading.Thread(target=self._jitter_loop, daemon=True)
            thread.start()
    
    def stop_jitter(self):
        """Stop the jitter"""
        self.is_running = False
    
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
                
                new_x = current_x + jitter_x
                new_y = current_y + jitter_y
                
                pyautogui.moveTo(new_x, new_y, duration=0.001)
                
                self.angle += (100 - self.jitter_speed) / 10
                if self.angle >= 360:
                    self.angle = 0
                
                sleep_time = (100 - self.jitter_speed) / 2000
                threading.Event().wait(sleep_time)
                
            except Exception as e:
                print(f"Error in jitter loop: {e}")
                self.is_running = False
    
    def _circular_pattern(self):
        """Circular jitter pattern - smooth circle movement"""
        radius = self.jitter_intensity
        angle_rad = math.radians(self.angle)
        
        jitter_x = int(radius * math.cos(angle_rad))
        jitter_y = int(radius * math.sin(angle_rad))
        
        return jitter_x, jitter_y
    
    def _figure8_pattern(self):
        """Figure-8 pattern - pro player micro-adjust"""
        t = math.radians(self.angle)
        a = self.jitter_intensity / 2
        
        denominator = 1 + math.sin(t) ** 2
        jitter_x = int((a * math.cos(t)) / denominator)
        jitter_y = int((a * math.sin(t) * math.cos(t)) / denominator)
        
        return jitter_x, jitter_y
    
    def _spiral_pattern(self):
        """Spiral pattern - expanding/contracting"""
        angle_rad = math.radians(self.angle)
        
        spiral_factor = (math.sin(self.angle / 180) + 1) / 2
        radius = self.jitter_intensity * spiral_factor
        
        jitter_x = int(radius * math.cos(angle_rad))
        jitter_y = int(radius * math.sin(angle_rad))
        
        return jitter_x, jitter_y
    
    def _zigzag_pattern(self):
        """Zigzag pattern - left-right micro-adjustments"""
        zigzag_x = int(self.jitter_intensity * math.sin(math.radians(self.angle)))
        zigzag_y = int(self.jitter_intensity * 0.3 * math.cos(math.radians(self.angle * 2)))
        
        return zigzag_x, zigzag_y
    
    def _wave_pattern(self):
        """Wave pattern - up-down tracking"""
        wave_y = int(self.jitter_intensity * math.sin(math.radians(self.angle)))
        wave_x = int(self.jitter_intensity * 0.3 * math.cos(math.radians(self.angle * 2)))
        
        return wave_x, wave_y


class MouseJitterApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.controller = JitterController()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Apex Aim Jitter - Easy Test Mode")
        self.setGeometry(100, 100, 600, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("APEX AIM JITTER TESTER")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Quick Start Info
        info = QLabel("Select a pattern → Adjust sliders → Click START → Test in game!")
        info_font = QFont()
        info_font.setPointSize(10)
        info.setFont(info_font)
        main_layout.addWidget(info)
        
        # Pattern Selection
        pattern_layout = QHBoxLayout()
        pattern_label = QLabel("Pattern:")
        pattern_label.setMinimumWidth(80)
        pattern_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        pattern_layout.addWidget(pattern_label)
        
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems(["Circular", "Figure-8", "Spiral", "Zigzag", "Wave"])
        self.pattern_combo.currentTextChanged.connect(self.update_pattern)
        self.pattern_combo.setStyleSheet("font-size: 11pt; padding: 5px;")
        pattern_layout.addWidget(self.pattern_combo)
        
        main_layout.addLayout(pattern_layout)
        
        # Intensity Slider
        intensity_layout = QHBoxLayout()
        intensity_label = QLabel("Intensity:")
        intensity_label.setMinimumWidth(80)
        intensity_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        intensity_layout.addWidget(intensity_label)
        
        self.intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.intensity_slider.setMinimum(1)
        self.intensity_slider.setMaximum(30)
        self.intensity_slider.setValue(5)
        self.intensity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.intensity_slider.setTickInterval(5)
        self.intensity_slider.valueChanged.connect(self.update_intensity)
        self.intensity_slider.setStyleSheet("font-size: 11pt;")
        intensity_layout.addWidget(self.intensity_slider)
        
        self.intensity_value = QLabel("5")
        self.intensity_value.setMinimumWidth(40)
        self.intensity_value.setStyleSheet("font-weight: bold; font-size: 11pt;")
        intensity_layout.addWidget(self.intensity_value)
        
        main_layout.addLayout(intensity_layout)
        
        # Speed Slider
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Speed:")
        speed_label.setMinimumWidth(80)
        speed_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        speed_layout.addWidget(speed_label)
        
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(50)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(10)
        self.speed_slider.valueChanged.connect(self.update_speed)
        self.speed_slider.setStyleSheet("font-size: 11pt;")
        speed_layout.addWidget(self.speed_slider)
        
        self.speed_value = QLabel("50")
        self.speed_value.setMinimumWidth(40)
        self.speed_value.setStyleSheet("font-weight: bold; font-size: 11pt;")
        speed_layout.addWidget(self.speed_value)
        
        main_layout.addLayout(speed_layout)
        
        # Pattern Info
        self.pattern_info = QLabel(
            "Circular: Smooth circular motion\n"
            "Figure-8: Pro player micro-adjust\n"
            "Spiral: Expanding/contracting\n"
            "Zigzag: Left-right adjustments\n"
            "Wave: Up-down tracking"
        )
        pattern_info_font = QFont()
        pattern_info_font.setPointSize(9)
        self.pattern_info.setFont(pattern_info_font)
        self.pattern_info.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        main_layout.addWidget(self.pattern_info)
        
        # Status
        self.status_label = QLabel("Status: STOPPED")
        status_font = QFont()
        status_font.setPointSize(12)
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        self.status_label.setStyleSheet("color: red; padding: 10px;")
        main_layout.addWidget(self.status_label)
        
        # Control Buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("▶ START JITTER")
        self.start_button.clicked.connect(self.start_jitter)
        self.start_button.setMinimumHeight(50)
        self.start_button.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; font-size: 12pt; border-radius: 5px;")
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("⏹ STOP JITTER")
        self.stop_button.clicked.connect(self.stop_jitter)
        self.stop_button.setMinimumHeight(50)
        self.stop_button.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold; font-size: 12pt; border-radius: 5px;")
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        main_layout.addLayout(button_layout)
        
        # Safety Info
        safety_label = QLabel("⚠️  Press ESC or move mouse to top-left corner to emergency stop")
        safety_font = QFont()
        safety_font.setPointSize(9)
        safety_label.setFont(safety_font)
        safety_label.setStyleSheet("color: #ff6b6b; padding: 10px;")
        main_layout.addWidget(safety_label)
        
        main_layout.addStretch()
        central_widget.setLayout(main_layout)
    
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
    
    def update_intensity(self, value):
        """Update jitter intensity"""
        self.controller.jitter_intensity = value
        self.intensity_value.setText(str(value))
    
    def update_speed(self, value):
        """Update jitter speed"""
        self.controller.jitter_speed = value
        self.speed_value.setText(str(value))
    
    def start_jitter(self):
        """Start jitter"""
        self.controller.start_jitter()
        self.status_label.setText("Status: RUNNING ✓")
        self.status_label.setStyleSheet("color: green; padding: 10px; font-weight: bold;")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.pattern_combo.setEnabled(False)
    
    def stop_jitter(self):
        """Stop jitter"""
        self.controller.stop_jitter()
        self.status_label.setText("Status: STOPPED")
        self.status_label.setStyleSheet("color: red; padding: 10px; font-weight: bold;")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.pattern_combo.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MouseJitterApp()
    window.show()
    sys.exit(app.exec())
