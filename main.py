import asyncio
import sys

from PyQt6.QtCore import Qt, QObject
from qasync import QEventLoop, QApplication, asyncSlot
from PyQt6.QtGui import QPalette, QColor


from database import db_manager
from gui.windows.login_window import LoginWindow
from gui.windows.main_window import MainWindow
from gui.windows.qr_login_window import QRLoginWindow
from database.db_manager import DatabaseManager
from services.http_client import AsyncHttpClient


class App(QObject):
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.loop = QEventLoop(self.app)
        asyncio.set_event_loop(self.loop)
        self.app.setStyle("Fusion")
        self.current_cookies = None

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        self.app.setPalette(palette)
        self.db_manager = DatabaseManager()
        self.http_client = AsyncHttpClient.instance()
        self.login_window = None
        self.main_window = None
        self.qr_window = None
        self.current_user_id = None

    async def start(self):
        try:
            self.login_window = LoginWindow()
            self.login_window.login_success.connect(self.handle_login_success)
            self.login_window.show()
            await self.loop.run_forever()
        except Exception as e:
            print(f"cuo_le:{str(e)}")

    async def cleanup(self):
        if hasattr(self, 'http_client'):
            await self.http_client.close()
        self.loop.stop()

    async def show_main_window(self):
        if self.login_window:
            self.login_window.close()
        if self.qr_window:
            self.qr_window.close()
        self.main_window = MainWindow(
            self.db_manager,
            self.current_user_id,
            self.current_cookies,
        )
        self.main_window.show()

    @asyncSlot()
    async def show_qr_login(self):
        try:
            if self.current_cookies:
                return await self.show_main_window()
            self.qr_window = QRLoginWindow(self.db_manager, self.current_user_id)
            self.qr_window.login_success.connect(self.handle_qr_success)
            self.qr_window.show()
        except Exception as e:
            print(f"二维码窗口错了: {e}")

    @asyncSlot(int, str)
    async def handle_login_success(self, user_id: int, cookies: str):
        self.current_user_id = user_id
        self.current_cookies = cookies
        await self.show_qr_login()

    @asyncSlot()
    async def handle_qr_success(self, status):
        if isinstance(status, dict):
            cookies = status.get('cookie')
            if cookies:
                print(f"爱还是得加: {cookies}")
                self.current_cookies = cookies
                if self.qr_window:
                    self.qr_window.close()
                await self.show_main_window()


async def main():
    app = App()
    try:
        await app.start()
    except Exception as e:
        print(f"程序出错: {e}")
    finally:
        await app.cleanup()


if __name__ == '__main__':
    asyncio.run(main())
