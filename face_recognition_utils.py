# face_recognition_utils.py
import cv2
import face_recognition
import numpy as np

def capture_video_stream():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Could not open webcam")
    return cap

def release_video_stream(cap):
    cap.release()

def get_frame(cap):
    ret, frame = cap.read()
    if not ret:
        raise Exception("Failed to read frame from webcam")
    return frame

def detect_faces(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    return face_locations, encodings

def draw_boxes(frame, face_locations, names=None, match_percentages=None):
    for i, (top, right, bottom, left) in enumerate(face_locations):
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        label = ""
        if names and i < len(names):
            label = names[i]
        if match_percentages and i < len(match_percentages):
            label += f" ({match_percentages[i]:.2f}%)"
        if label:
            cv2.putText(frame, label, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2)
    return frame
