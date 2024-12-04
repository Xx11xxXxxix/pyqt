import sys
import random
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox)
from PyQt6.QtCore import QTimer, pyqtSignal,QObject
from database.db_manager import DatabaseManager

class LoginWindow(QWidget):
    # login_success = pyqtSignal(name='login_success')
    login_success = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        try:
            self.db = DatabaseManager()
            self.verification_code = ""
            self.init_ui()
        except Exception as e:
            print(f"登录窗口初始化错误: {e}")

    def init_ui(self):
        self.setWindowTitle('账号登录')
        self.setFixedSize(200, 140)

        # 创建主布局
        layout = QVBoxLayout()


        # 手机号输入
        mobile_layout = QHBoxLayout()
        mobile_label = QLabel('手机号:')
        self.mobile_input = QLineEdit()
        self.mobile_input.setMaxLength(11)
        mobile_layout.addWidget(mobile_label)
        mobile_layout.addWidget(self.mobile_input)

        # 验证码输入和获取按钮
        code_layout = QHBoxLayout()
        code_label = QLabel('验证码:')
        self.code_input = QLineEdit()
        self.code_input.setMaxLength(4)
        self.get_code_btn = QPushButton('获取验证码')
        self.get_code_btn.clicked.connect(self.generate_verification_code)
        code_layout.addWidget(code_label)
        code_layout.addWidget(self.code_input)
        code_layout.addWidget(self.get_code_btn)

        # 登录按钮
        self.login_btn = QPushButton('登录')
        self.login_btn.clicked.connect(self.verify_login)

        # 添加所有组件到主布局
        layout.addLayout(mobile_layout)
        layout.addLayout(code_layout)
        layout.addWidget(self.login_btn)

        # 设置布局
        self.setLayout(layout)

    def generate_verification_code(self):
        # self.verification_code = str(random.randint(1000, 9999))
        self.verification_code = str(1234)
        print(self.verification_code)
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
            self.get_code_btn.setText('获取验证码')
        else:
            self.get_code_btn.setText(f'重新获取({self.countdown})')

    def verify_login(self):
        mobile = self.mobile_input.text().strip()
        code = self.code_input.text().strip()
        if code != self.verification_code:
            QMessageBox.warning(self, '提示', '验证码错误')
            return
        user_id = self.db.add_or_update_user(mobile)
        QMessageBox.information(self, '成功', 'Gooin')
        self.login_success.emit(user_id)
