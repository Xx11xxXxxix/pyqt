import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication

from database import db_manager
from gui.windows.login_window import LoginWindow
from gui.windows.qr_login_window import QRLoginWindow
from database.db_manager import DatabaseManager

class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")
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
        self.login_window = None
        self.main_window = None
        self.qr_window = None
        self.current_user_id = None

    def start(self):
        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self.show_qr_login)
        self.login_window.show()
        return self.app.exec()

    def show_main_window(self):
        self.login_window.close()

    def show_qr_login(self):
        try:
            self.qr_window = QRLoginWindow(self.db_manager, self.current_user_id)
            self.qr_window.login_success.connect(self.handle_login_success)
            self.qr_window.show()
        except Exception as e:
            print(f"打开二维码窗口错误: {e}")

    def handle_login_success(self, user_id):
        self.current_user_id = user_id
        self.show_qr_login()
if __name__ == '__main__':
    try:
        app = App()
        sys.exit(app.start())
    except Exception as e:
        print(f"程序出错: {e}")