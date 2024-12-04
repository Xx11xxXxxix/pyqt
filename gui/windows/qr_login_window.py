import json
import sys
import requests
import base64
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QMessageBox)
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap
from io import BytesIO


class QRLoginWindow(QWidget):
    login_success = pyqtSignal(dict)  # 登录成功信号
    BASE_URL = "http://127.0.0.1:3000"
    def __init__(self, db_manager,user_id):
        super().__init__()
        self.db_manager = db_manager
        self.user_id = user_id
        self.unikey = None
        self.init_ui()
        self.get_qr_code()
        # 初始化定时器
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_scan_status)
        self.check_timer.start(2000)  # 每2秒检查一次

    def init_ui(self):
        self.setWindowTitle('扫码登录')
        self.setFixedSize(300, 400)

        layout = QVBoxLayout()

        # 二维码标签
        self.qr_label = QLabel()
        self.qr_label.setFixedSize(280, 280)
        layout.addWidget(self.qr_label)

        # 状态标签
        self.status_label = QLabel('请使用网易云音乐APP扫码登录')
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def get_qr_code(self):
        try:
            # 获取unikey
            response = requests.get(f"{self.BASE_URL}/login/qr/key")
            self.db_manager.log_api_call(
                user_id=self.user_id,
                api_name='login_qr_key',
                request_params=json.dumps({}),
                response_data=json.dumps(response.json()),
                status_code=response.status_code
            )

            if response.status_code != 200:
                self.status_label.setText('获取二维码失败')
                return

            self.unikey = response.json()["data"]["unikey"]

            # 获取二维码图片
            response = requests.get(f"{self.BASE_URL}/login/qr/create",
                                    params={'key': self.unikey, 'qrimg': True})
            self.db_manager.log_api_call(
                user_id=self.user_id,
                api_name='login_qr_create',
                request_params=json.dumps({'key': self.unikey}),
                response_data=json.dumps(response.json()),
                status_code=response.status_code
            )
            if response.status_code != 200:
                self.status_label.setText('获取二维码失败')
                return

            qrimg = response.json()["data"]["qrimg"]
            qr_bytes = base64.b64decode(qrimg.split(",")[1])
            qr_image = BytesIO(qr_bytes)

            # 显示二维码
            pixmap = QPixmap()
            pixmap.loadFromData(qr_bytes)
            self.qr_label.setPixmap(pixmap.scaled(280, 280))

        except Exception as e:
            self.status_label.setText(f'错误: {str(e)}')
            self.db_manager.log_api_call(
                'qr_code_error',
                {},
                {'error': str(e)},
                500,
                str(e)
            )

    def check_scan_status(self):
        if not self.unikey:
            return

        try:
            response = requests.get(f"{self.BASE_URL}/login/qr/check",
                                    params={'key': self.unikey})

            self.db_manager.log_api_call(
                user_id=self.user_id,
                api_name='login_qr_create',
                request_params=json.dumps({'key': self.unikey}),
                response_data=json.dumps(response.json()),
                status_code=response.status_code
            )

            if response.status_code != 200:
                return

            status = response.json()
            code = status.get('code')

            if code == 800:
                self.status_label.setText('二维码已过期，请刷新')
                self.get_qr_code()
            elif code == 801:
                self.status_label.setText('等待扫码')
            elif code == 802:
                self.status_label.setText('扫码成功，等待确认')
            elif code == 803:
                self.status_label.setText('登录成功！')
                self.check_timer.stop()
                self.login_success.emit(status)
                self.close()

        except Exception as e:
            self.status_label.setText(f'检查状态出错: {str(e)}')
            self.db_manager.log_api_call(
                'status_check_error',
                {'key': self.unikey},
                {'error': str(e)},
                500,
                str(e)
            )