# register.py
import sys
from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QLabel, 
                             QInputDialog, QMessageBox, QHBoxLayout, QScrollArea, QLineEdit)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer
import cv2
from face_recognition_utils import capture_video_stream, release_video_stream, get_frame, detect_faces, draw_boxes
from database import add_user

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register User")
        self.setGeometry(150, 150, 800, 600)
        self.face_encodings = []
        self.name_inputs = []
        self.setup_ui()
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def setup_ui(self):
        layout = QVBoxLayout()

        self.capture_btn = QPushButton("Start Registration")
        self.capture_btn.clicked.connect(self.start_registration)

        self.image_label = QLabel("Live Video Feed")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(640, 480)

        layout.addWidget(self.capture_btn)
        layout.addWidget(self.image_label)

        self.setLayout(layout)

    def start_registration(self):
        try:
            self.cap = capture_video_stream()
            self.timer.start(30)  # Update every 30 ms
            self.capture_btn.setText("Capture and Register")
            self.capture_btn.clicked.disconnect()
            self.capture_btn.clicked.connect(self.capture_and_process)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_frame(self):
        try:
            frame = get_frame(self.cap)
            face_locations, encodings = detect_faces(frame)
            annotated_frame = draw_boxes(frame.copy(), face_locations, names=None)
            # Convert to QImage and display
            rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.timer.stop()
            release_video_stream(self.cap)
            self.cap = None

    def capture_and_process(self):
        self.timer.stop()
        try:
            frame = get_frame(self.cap)
            release_video_stream(self.cap)
            self.cap = None
            face_locations, encodings = detect_faces(frame)
            if not face_locations:
                QMessageBox.warning(self, "No Faces Detected", "No faces were detected in the image.")
                self.capture_btn.setText("Start Registration")
                self.capture_btn.clicked.disconnect()
                self.capture_btn.clicked.connect(self.start_registration)
                return
            self.face_encodings = encodings
            # Draw boxes and prompt for names
            annotated_frame = draw_boxes(frame.copy(), face_locations)
            # Convert to RGB for display
            rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))
            # Prompt for names
            self.name_inputs = []
            for i in range(len(face_locations)):
                name, ok = QInputDialog.getText(self, f"Name for Face {i+1}", "Enter name:")
                if ok and name.strip():
                    self.name_inputs.append(name.strip())
                else:
                    QMessageBox.warning(self, "Input Error", "Name input was cancelled or empty.")
                    self.capture_btn.setText("Start Registration")
                    self.capture_btn.clicked.disconnect()
                    self.capture_btn.clicked.connect(self.start_registration)
                    return
            self.submit_registration()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.capture_btn.setText("Start Registration")
            self.capture_btn.clicked.disconnect()
            self.capture_btn.clicked.connect(self.start_registration)

    def submit_registration(self):
        if len(self.name_inputs) != len(self.face_encodings):
            QMessageBox.warning(self, "Mismatch", "Number of names and faces do not match.")
            return
        try:
            for name, encoding in zip(self.name_inputs, self.face_encodings):
                add_user(name, encoding)
            QMessageBox.information(self, "Success", "User(s) registered successfully.")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def closeEvent(self, event):
        if self.cap:
            self.timer.stop()
            release_video_stream(self.cap)
        event.accept()
