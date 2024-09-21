# login.py
import sys
from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QLabel, 
                             QMessageBox)
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import Qt, QTimer
import cv2
import face_recognition
from face_recognition_utils import capture_video_stream, release_video_stream, get_frame, detect_faces, draw_boxes
from database import get_all_users
import numpy as np

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("User Login")
        self.setGeometry(150, 150, 800, 600)
        self.setup_ui()
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.users = get_all_users()
        self.known_encodings = [user[1] for user in self.users]
        self.known_names = [user[0] for user in self.users]

    def setup_ui(self):
        layout = QVBoxLayout()

        self.capture_btn = QPushButton("Start Login")
        self.capture_btn.clicked.connect(self.start_login)

        self.image_label = QLabel("Live Video Feed")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(640, 480)

        self.greeting_label = QLabel("")
        self.greeting_label.setAlignment(Qt.AlignCenter)
        self.greeting_label.setFont(QFont('Arial', 16))
        self.greeting_label.setStyleSheet("color: #27ae60;")

        layout.addWidget(self.capture_btn)
        layout.addWidget(self.image_label)
        layout.addWidget(self.greeting_label)

        self.setLayout(layout)

    def start_login(self):
        try:
            self.cap = capture_video_stream()
            self.timer.start(30)  # Update every 30 ms
            self.capture_btn.setText("Capture and Login")
            self.capture_btn.clicked.disconnect()
            self.capture_btn.clicked.connect(self.capture_and_recognize)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_frame(self):
        try:
            frame = get_frame(self.cap)
            face_locations, encodings = detect_faces(frame)
            annotated_frame = frame.copy()
            names = []
            match_percentages = []
            for encoding in encodings:
                matches = face_recognition.compare_faces(self.known_encodings, encoding)
                distances = face_recognition.face_distance(self.known_encodings, encoding)
                best_match_index = np.argmin(distances) if distances.size > 0 else -1
                if best_match_index != -1 and matches[best_match_index]:
                    name = self.known_names[best_match_index]
                    # Calculate percentage (inverse of distance)
                    percentage = (1 - distances[best_match_index]) * 100
                else:
                    name = "Unknown"
                    percentage = 0.0
                names.append(name)
                match_percentages.append(percentage)
            annotated_frame = draw_boxes(frame.copy(), face_locations, names, match_percentages)
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

    def capture_and_recognize(self):
        self.timer.stop()
        try:
            frame = get_frame(self.cap)
            release_video_stream(self.cap)
            self.cap = None
            face_locations, encodings = detect_faces(frame)
            if len(face_locations) != 1:
                QMessageBox.warning(self, "Invalid Number of Faces", "Please ensure exactly one face is in the image.")
                self.capture_btn.setText("Start Login")
                self.capture_btn.clicked.disconnect()
                self.capture_btn.clicked.connect(self.start_login)
                return
            encoding = encodings[0]
            # Recognition
            matches = face_recognition.compare_faces(self.known_encodings, encoding)
            distances = face_recognition.face_distance(self.known_encodings, encoding)
            best_match_index = np.argmin(distances) if distances.size > 0 else -1
            if best_match_index != -1 and matches[best_match_index]:
                name = self.known_names[best_match_index]
                percentage = (1 - distances[best_match_index]) * 100
            else:
                name = "Unknown"
                percentage = 0.0
            # Annotate frame
            annotated_frame = draw_boxes(frame.copy(), face_locations, [name], [percentage])
            # Convert to QImage and display
            rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))
            # Greet user
            if name != "Unknown":
                self.greeting_label.setText(f"Hello, {name}! ({percentage:.2f}% match)")
            else:
                self.greeting_label.setText("Hello, Unknown User!")
            self.capture_btn.setText("Start Login")
            self.capture_btn.clicked.disconnect()
            self.capture_btn.clicked.connect(self.start_login)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.capture_btn.setText("Start Login")
            self.capture_btn.clicked.disconnect()
            self.capture_btn.clicked.connect(self.start_login)

    def closeEvent(self, event):
        if self.cap:
            self.timer.stop()
            release_video_stream(self.cap)
        event.accept()
