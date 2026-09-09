import sys
import threading
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QPushButton, QSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QFont
import pyautogui

# Disable pyautogui safety features
pyautogui.FAILSAFE = False


class JitterController(QObject):
    """Handles mouse jitter logic"""
    
    def __init__(self):
        super().__init__()
        self.is_running = False
        self.jitter_intensity = 5
        self.jitter_speed = 50
        self.update_interval = 10
        
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
        """Main jitter loop"""
        while self.is_running:
            try:
                # Get current mouse position
                current_x, current_y = pyautogui.position()
                
                # Calculate random jitter offset
                jitter_x = random.randint(-self.jitter_intensity, self.jitter_intensity)
                jitter_y = random.randint(-self.jitter_intensity, self.jitter_intensity)
                
                # Apply jitter
                new_x = current_x + jitter_x
                new_y = current_y + jitter_y
                
                pyautogui.moveTo(new_x, new_y, duration=0.001)
                
                # Control speed (higher speed value = faster jitter)
                sleep_time = (100 - self.jitter_speed) / 1000
                threading.Event().wait(sleep_time)
                
            except Exception as e:
                print(f"Error in jitter loop: {e}")
                self.is_running = False


class MouseJitterApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.controller = JitterController()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Mouse Jitter App")
        self.setGeometry(100, 100, 500, 400)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Mouse Jitter Controller")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Jitter Intensity Slider
        intensity_layout = QHBoxLayout()
        intensity_label = QLabel("Jitter Intensity:")
        intensity_label.setMinimumWidth(120)
        intensity_layout.addWidget(intensity_label)
        
        self.intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.intensity_slider.setMinimum(1)
        self.intensity_slider.setMaximum(50)
        self.intensity_slider.setValue(5)
        self.intensity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.intensity_slider.setTickInterval(5)
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
        
        # Info
        info_label = QLabel("⚠️  Move mouse to top-left corner to emergency stop")
        info_font = QFont()
        info_font.setPointSize(9)
        info_label.setFont(info_font)
        main_layout.addWidget(info_label)
        
        main_layout.addStretch()
        central_widget.setLayout(main_layout)
    
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
    
    def stop_jitter(self):
        """Stop jitter"""
        self.controller.stop_jitter()
        self.status_label.setText("Status: Stopped")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MouseJitterApp()
    window.show()
    sys.exit(app.exec())