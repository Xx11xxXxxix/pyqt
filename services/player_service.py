from PyQt6.QtCore import QObject, pyqtSignal, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput


class PlayerService(QObject):
    _instance = None
    playback_state_changed = pyqtSignal(bool)  # 播放状态信号
    position_changed = pyqtSignal(int)  # 播放位置的信号这个牛逼
    duration_changed = pyqtSignal(int)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls.instance=cls()
        return cls.instance


    def __init__(self):
        super().__init__()
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.positionChanged.connect(self._on_position_changed)
        self.media_player.durationChanged.connect(self._on_duration_changed)

    def play_url(self, url: str):
        print(1)
        self.media_player.setSource(QUrl(url))
        self.media_player.play()

    def play_pause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def stop(self):
        self.media_player.stop()

    def set_volume(self, volume: int):
        self.audio_output.setVolume(volume / 100)

    def set_position(self, position: int):
        self.media_player.setPosition(position)

    def _on_position_changed(self, position: int):
        self.position_changed.emit(position)

    def _on_duration_changed(self, duration: int):
        self.duration_changed.emit(duration)