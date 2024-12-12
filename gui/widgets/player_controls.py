from PyQt6.QtGui import QIcon
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSlider, QLabel
from PyQt6.QtCore import Qt
from services.player_service import PlayerService
from services.recommend_songs import RecommendAPI


class PlayerControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.player_service = PlayerService()
        self.recommend_api=RecommendAPI()
        self.play_mode = PlayMode.SEQUENCE

        self.playlist=[]
        self.current_index=-1

        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        layout = QHBoxLayout(self)

        self.play_button = QPushButton('打灭')
        self.next_button=QPushButton('下一首')
        self.prev_button=QPushButton('上一首')


        self.play_button.clicked.connect(self.player_service.play_pause)
        self.next_button.clicked.connect(self.play_next)
        self.prev_button.clicked.connect(self.play_previous)

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
        layout.addWidget(self.next_button)
        layout.addWidget(self.prev_button)
        self.is_muted = False
        self.last_volume = 50


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

    def add_to_playlist(self, song):
        """添加歌曲到播放列表"""
        self.playlist.append(song)

    def set_playlist(self, songs):
        """设置整个播放列表"""
        self.playlist = songs
        self.current_index = -1

    def clear_playlist(self):
        """清空播放列表"""
        self.playlist = []
        self.current_index = -1

    def play_next(self):
        print(111)
        """播放下一首"""
        if not self.playlist:
            return

        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play_current_song()

    def play_previous(self):
        """播放上一首"""
        if not self.playlist:
            return

        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play_current_song()

    def play_current_song(self):
        """播放当前索引的歌曲"""
        if 0 <= self.current_index < len(self.playlist):
            current_song = self.playlist[self.current_index]
            song_id = current_song.get('id')
            if song_id:
                self.recommend_api.get_songs_url(song_id)

    def connect_signals(self):
        self.player_service.position_changed.connect(self.update_position)
        self.player_service.duration_changed.connect(self.update_duration)

        self.player_service.media_player.mediaStatusChanged.connect(self.on_media_status_changed)

    def on_media_status_changed(self, status):
        """监听播放状态变化"""
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            # 播放完成时自动播放下一首
            self.play_next()

    def set_play_mode(self, mode):
        self.play_mode = mode

    @staticmethod
    def format_time(ms):
        s = round(ms / 1000)
        m, s = divmod(s, 60)
        return f'{m:02d}:{s:02d}'




class PlayMode:
    SEQUENCE = 0  # 顺序播放
    LOOP = 1  # 列表循环
    SINGLE = 2  # 单曲循环
    RANDOM = 3  # 随机播放


