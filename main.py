# main.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QIcon
from register import RegisterWindow
from login import LoginWindow
from database import initialize_db

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Login Application")
        self.setGeometry(100, 100, 400, 200)
        self.setWindowIcon(QIcon('resources/icons/app_icon.png'))
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.register_btn = QPushButton("Register")
        self.register_btn.setIcon(QIcon('resources/icons/register.png'))
        self.register_btn.clicked.connect(self.open_register)

        self.login_btn = QPushButton("Login")
        self.login_btn.setIcon(QIcon('resources/icons/login.png'))
        self.login_btn.clicked.connect(self.open_login)

        layout.addStretch()
        layout.addWidget(self.register_btn)
        layout.addWidget(self.login_btn)
        layout.addStretch()

        self.setLayout(layout)

    def open_register(self):
        self.register_window = RegisterWindow()
        self.register_window.show()

    def open_login(self):
        self.login_window = LoginWindow()
        self.login_window.show()

if __name__ == "__main__":
    initialize_db()
    app = QApplication(sys.argv)
    # Apply stylesheet
    with open('resources/styles/style.qss', 'r') as f:
        app.setStyleSheet(f.read())
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
