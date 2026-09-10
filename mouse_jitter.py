import sys
import threading
import random
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
        self.pattern_type = "circular"  # circular, figure8, spiral
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
                # Get current mouse position
                current_x, current_y = pyautogui.position()
                
                # Calculate jitter based on pattern type
                if self.pattern_type == "circular":
                    jitter_x, jitter_y = self._circular_pattern()
                elif self.pattern_type == "figure8":
                    jitter_x, jitter_y = self._figure8_pattern()
                elif self.pattern_type == "spiral":
                    jitter_x, jitter_y = self._spiral_pattern()
                else:
                    jitter_x, jitter_y = self._circular_pattern()
                
                # Apply jitter
                new_x = current_x + jitter_x
                new_y = current_y + jitter_y
                
                pyautogui.moveTo(new_x, new_y, duration=0.001)
                
                # Increment angle for smooth patterns
                self.angle += (100 - self.jitter_speed) / 10
                if self.angle >= 360:
                    self.angle = 0
                
                # Control speed
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
        """Figure-8 pattern - used by pro Apex players for precise tracking"""
        # Lemniscate (figure-8) curve
        t = math.radians(self.angle)
        a = self.jitter_intensity / 2
        
        # Parametric equation for figure-8
        denominator = 1 + math.sin(t) ** 2
        jitter_x = int((a * math.cos(t)) / denominator)
        jitter_y = int((a * math.sin(t) * math.cos(t)) / denominator)
        
        return jitter_x, jitter_y
    
    def _spiral_pattern(self):
        """Spiral pattern - expanding/contracting circular movement"""
        angle_rad = math.radians(self.angle)
        
        # Create spiral effect by varying radius
        spiral_factor = (math.sin(self.angle / 180) + 1) / 2
        radius = self.jitter_intensity * spiral_factor
        
        jitter_x = int(radius * math.cos(angle_rad))
        jitter_y = int(radius * math.sin(angle_rad))
        
        return jitter_x, jitter_y


class MouseJitterApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.controller = JitterController()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Apex Aim Jitter Controller")
        self.setGeometry(100, 100, 550, 450)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Apex Aim Jitter Controller")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Pattern Type Selection
        pattern_layout = QHBoxLayout()
        pattern_label = QLabel("Jitter Pattern:")
        pattern_label.setMinimumWidth(120)
        pattern_layout.addWidget(pattern_label)
        
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems(["Circular", "Figure-8", "Spiral"])
        self.pattern_combo.currentTextChanged.connect(self.update_pattern)
        pattern_layout.addWidget(self.pattern_combo)
        
        main_layout.addLayout(pattern_layout)
        
        # Jitter Intensity Slider
        intensity_layout = QHBoxLayout()
        intensity_label = QLabel("Jitter Intensity:")
        intensity_label.setMinimumWidth(120)
        intensity_layout.addWidget(intensity_label)
        
        self.intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.intensity_slider.setMinimum(1)
        self.intensity_slider.setMaximum(30)
        self.intensity_slider.setValue(5)
        self.intensity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.intensity_slider.setTickInterval(3)
        self.intensity_slider.valueChanged.connect(self.update_intensity)
        intensity_layout.addWidget(self.intensity_slider)
        
        self.intensity_value = QLabel("5")
        self.intensity_value.setMinimumWidth(30)
        intensity_layout.addWidget(self.intensity_value)
        
        main_layout.addLayout(intensity_layout)
        
        # Jitter Speed Slider
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Jitter Speed:")
        speed_label.setMinimumWidth(120)
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
        self.speed_value.setMinimumWidth(30)
        speed_layout.addWidget(self.speed_value)
        
        main_layout.addLayout(speed_layout)
        
        # Info about patterns
        info_label = QLabel(
            "Circular: Smooth circular motion\n"
            "Figure-8: Pro player micro-adjust pattern\n"
            "Spiral: Expanding/contracting movement"
        )
        info_font = QFont()
        info_font.setPointSize(9)
        info_label.setFont(info_font)
        main_layout.addWidget(info_label)
        
        # Status
        self.status_label = QLabel("Status: Stopped")
        status_font = QFont()
        status_font.setPointSize(11)
        self.status_label.setFont(status_font)
        main_layout.addWidget(self.status_label)
        
        # Control Buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Jitter")
        self.start_button.clicked.connect(self.start_jitter)
        self.start_button.setMinimumHeight(40)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Jitter")
        self.stop_button.clicked.connect(self.stop_jitter)
        self.stop_button.setMinimumHeight(40)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        main_layout.addLayout(button_layout)
        
        # Safety warning
        warning_label = QLabel("⚠️  Move mouse to top-left corner to emergency stop")
        warning_font = QFont()
        warning_font.setPointSize(9)
        warning_label.setFont(warning_font)
        main_layout.addWidget(warning_label)
        
        main_layout.addStretch()
        central_widget.setLayout(main_layout)
    
    def update_pattern(self, pattern_name):
        """Update jitter pattern type"""
        pattern_map = {
            "Circular": "circular",
            "Figure-8": "figure8",
            "Spiral": "spiral"
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
        self.status_label.setText("Status: Running ✓")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.pattern_combo.setEnabled(False)
    
    def stop_jitter(self):
        """Stop jitter"""
        self.controller.stop_jitter()
        self.status_label.setText("Status: Stopped")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.pattern_combo.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MouseJitterApp()
    window.show()
    sys.exit(app.exec())
