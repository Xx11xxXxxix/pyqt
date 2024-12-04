import sys
import random
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox)
from PyQt6.QtCore import QTimer, pyqtSignal, QObject
from database.db_manager import DatabaseManager


class LoginWindow(QWidget):
    # login_success = pyqtSignal(name='login_success')
    login_success = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()
        try:
            self.db = DatabaseManager()
            self.verification_code = ""
            self.init_ui()
        except Exception as e:
            print(f"登录窗口八错: {e}")

    def init_ui(self):
        self.setWindowTitle('朱的浩')
        self.setFixedSize(200, 140)

        # 主页面
        layout = QVBoxLayout()

        mobile_layout = QHBoxLayout()
        mobile_label = QLabel('手机的阿红:')
        self.mobile_input = QLineEdit()
        self.mobile_input.setMaxLength(11)
        mobile_layout.addWidget(mobile_label)
        mobile_layout.addWidget(self.mobile_input)
        code_layout = QHBoxLayout()
        code_label = QLabel('验证D吗:')
        self.code_input = QLineEdit()
        self.code_input.setMaxLength(4)
        self.get_code_btn = QPushButton('点几把验证码')
        self.get_code_btn.clicked.connect(self.generate_verification_code)
        code_layout.addWidget(code_label)
        code_layout.addWidget(self.code_input)
        code_layout.addWidget(self.get_code_btn)

        self.login_btn = QPushButton('go')
        self.login_btn.clicked.connect(self.verify_login)

        layout.addLayout(mobile_layout)
        layout.addLayout(code_layout)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def generate_verification_code(self):
        # self.verification_code = str(random.randint(1000, 9999))
        self.verification_code = str(1234)
        self.get_code_btn.setEnabled(False)
        self.countdown = 60
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_button)
        self.timer.start(1000)

    def update_button(self):
        self.countdown -= 1
        if self.countdown <= 0:
            self.timer.stop()
            self.get_code_btn.setEnabled(True)
            self.get_code_btn.setText('验证那')
        else:
            self.get_code_btn.setText(f'再来({self.countdown})')

    def verify_login(self):
        try:
            mobile = self.mobile_input.text().strip()
            code = self.code_input.text().strip()
            if code != self.verification_code:
                QMessageBox.warning(self, 'sb', '这都能填错啊')
                return

            user_id = self.db.add_or_update_user(mobile)
            print(f"user_id: {user_id}")

            cookies = self.db.get_user_cookies(user_id)
            print(f"cookies: {cookies}")

            if cookies:
                QMessageBox.information(self, '1', 'youcookie')
                try:
                    self.login_success.emit(user_id, cookies)
                    print("有信号 - 有cookies")
                except Exception as e:
                    print(f"没信号 - 有cookies: {str(e)}")
            else:
                QMessageBox.information(self, '1', 'go')
                try:
                    self.login_success.emit(user_id, "")
                    print("有信号 - 无cookies")
                except Exception as e:
                    print(f"信号没了 - 无cookies: {str(e)}")

        except Exception as e:
            print(f"验证码几把错了吗: {str(e)}")
            QMessageBox.warning(self, '操', f'登录接口错了: {str(e)}')
