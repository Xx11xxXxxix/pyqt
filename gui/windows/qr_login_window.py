import json
import sys
import requests
import base64
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QMessageBox)
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap
from io import BytesIO


class QRLoginWindow(QWidget):
    login_success = pyqtSignal(dict)  # 登上的信号
    BASE_URL = "http://121.36.9.139:3000"

    def __init__(self, db_manager, user_id):
        super().__init__()
        self.db_manager = db_manager
        self.user_id = user_id
        self.unikey = None
        self.init_ui()
        self.get_qr_code()
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_scan_status)
        self.check_timer.start(2000)

    def closeEvent(self, event):
        # 登上了哈几把一直伦
        self.check_timer.stop()
        super().closeEvent(event)

    def init_ui(self):
        self.setWindowTitle('扫码登录')
        self.setFixedSize(300, 400)

        layout = QVBoxLayout()

        self.qr_label = QLabel()
        self.qr_label.setFixedSize(280, 280)
        layout.addWidget(self.qr_label)
        self.status_label = QLabel('扫吗')
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def get_qr_code(self):
        try:
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

            pixmap = QPixmap()
            pixmap.loadFromData(qr_bytes)
            self.qr_label.setPixmap(pixmap.scaled(280, 280))

        except Exception as e:
            self.status_label.setText(f'错偶尔: {str(e)}')
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
            data = response.json()
            code = data.get('code')
            if code == 803:
                print(803)
                cookie = data.get('cookie', '')
                music_u = self.extract_music_u(cookie)
                if music_u:
                    self.db_manager.update_user_cookies(self.user_id, music_u)
                    self.check_timer.stop()
                    self.login_success.emit(data)
                    self.close()
            elif code == 800:
                self.status_label.setText('guoqi')
                self.get_qr_code()
        except Exception as e:
            self.status_label.setText(f'轮询报错了: {str(e)}')
            self.db_manager.log_api_call(
                'status_check_error',
                {'key': self.unikey},
                {'error': str(e)},
                500,
                str(e)
            )

    def extract_music_u(self, cookie_str: str) -> str:
        try:
            cookies = cookie_str.split(';')
            for cookie in cookies:
                if 'MUSIC_U=' in cookie:
                    music_u = cookie.strip()
                    print(f"有MUSIC_U: {music_u[:20]}...")
                    return music_u
            print("没有啊")
            return ''
        except Exception as e:
            print(f"操了: {e}")
            return ''
