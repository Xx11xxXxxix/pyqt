from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSignal
class SongContextMenu(QMenu):
    show_first_listen_info = pyqtSignal(int)

    def __init__(self, song_id, parent=None):
        super().__init__(parent)
        self.song_id = song_id
        self.init_actions()

    def init_actions(self):
        first_listen_action = QAction("音乐是记忆的载体", self)
        first_listen_action.triggered.connect(self.on_first_listen_clicked)
        self.addAction(first_listen_action)

    def on_first_listen_clicked(self):
        self.show_first_listen_info.emit(self.song_id)