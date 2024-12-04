from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSlider, QLabel
from PyQt6.QtCore import Qt
from services.player_service import PlayerService


class PlayerControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.player_service = PlayerService()
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        layout = QHBoxLayout(self)

        self.play_button = QPushButton('打灭')
        self.play_button.clicked.connect(self.player_service.play_pause)

        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.sliderMoved.connect(self.player_service.set_position)

        self.volume_icon = QPushButton()
        self.volume_icon.setIcon(QIcon("gui/styles/icons/volume.png"))
        self.volume_icon.setFixedSize(24, 24)
        self.volume_icon.clicked.connect(self.toggle_mute)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)

        self.time_label = QLabel('00:00 / 00:00')

        layout.addWidget(self.play_button)
        layout.addWidget(self.time_label)
        layout.addWidget(self.position_slider)
        layout.addWidget(self.volume_slider)
        layout.addWidget(self.volume_icon)
        self.is_muted = False
        self.last_volume = 50
    def connect_signals(self):
        self.player_service.position_changed.connect(self.update_position)
        self.player_service.duration_changed.connect(self.update_duration)

    def toggle_mute(self):
        if self.is_muted:
            self.volume_slider.setValue(self.last_volume)
            self.volume_icon.setIcon(QIcon("gui/styles/icons/volume.png"))
        else:
            self.last_volume = self.volume_slider.value()
            self.volume_slider.setValue(0)
            self.volume_icon.setIcon(QIcon("gui/styles/icons/mute.png"))
        self.is_muted = not self.is_muted

    def on_volume_changed(self, value):
        self.player_service.set_volume(value)
        # 更新图标状态
        if value == 0:
            self.volume_icon.setIcon(QIcon("gui/styles/icons/mute.png"))
            self.is_muted = True
        else:
            self.volume_icon.setIcon(QIcon("gui/styles/icons/volume.png"))
            self.is_muted = False

    def update_position(self, position):
        self.position_slider.setValue(position)
        current = self.format_time(position)
        duration = self.format_time(self.player_service.media_player.duration())
        self.time_label.setText(f'{current} / {duration}')

    def update_duration(self, duration):
        self.position_slider.setRange(0, duration)

    @staticmethod
    def format_time(ms):
        s = round(ms / 1000)
        m, s = divmod(s, 60)
        return f'{m:02d}:{s:02d}'
