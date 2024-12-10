from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QTimer


class Toast(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedWidth(200)

    @staticmethod
    def show_message(parent, message, duration=1000):
        """
        Args:
            parent: 父窗口
            message: 提示信息
            duration: 显示时间(毫秒)
        """
        # 移除旧提示
        for child in parent.children():
            if isinstance(child, Toast):
                child.deleteLater()

        toast = Toast(parent)
        toast.setText(message)

        # 计算位置（窗口底部居中）
        x = (parent.width() - toast.width()) // 2
        y = parent.height() - 80
        toast.move(x, y)
        toast.show()
        # 自动隐藏
        QTimer.singleShot(duration, toast.deleteLater)