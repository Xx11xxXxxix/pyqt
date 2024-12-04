import requests
import json

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QListWidget, QLabel, QPushButton

from services.recommend_songs import RecommendAPI
from gui.widgets.player_controls import PlayerControls

class MainWindow(QMainWindow):
    def __init__(self, db_manager, user_id, cookies):
        super().__init__()
        self.db_manager = db_manager
        self.user_id = user_id
        self.cookies = cookies
        self.recommend_api = RecommendAPI.instance()
        self.recommend_api.set_cookies(cookies)

        self.BASE_URL = "http://127.0.0.1:3000"
        self.init_ui()
        self.recommend_api.daily_songs_received.connect(self.on_daily_songs_received)
        self.recommend_api.song_url_received.connect(self.on_song_url_received)
        self.is_requesting = False

    def init_ui(self):
        self.setWindowTitle('已闻君，诸事安康。 遇佳人，不久婚嫁。 已闻君，得偿所想。 料得是，卿识君望')
        self.setGeometry(100, 100, 800, 600)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        self.player_controls = PlayerControls()
        self.song_list = QListWidget()
        self.status_label = QLabel('SENDIT!!!!!')
        self.get_recommend_btn = QPushButton('不主动就是不喜欢了[多多捂脸]')
        self.get_recommend_btn.clicked.connect(self.get_daily_songs)

        layout.addWidget(self.get_recommend_btn)

        layout.addWidget(self.song_list)
        layout.addWidget(self.player_controls)
        layout.addWidget(self.status_label)

        # self.get_recommend_btn.clicked.connect(self.get_daily_songs)
        self.song_list.itemClicked.connect(self.on_song_clicked)

    def get_daily_songs(self):
        if self.is_requesting:
            print("卧槽重复请求了一会闪退")
            return

        try:
            self.is_requesting = True
            self.status_label.setText('等着...')
            self.recommend_api.get_daily_songs()
        except Exception as e:
            print(f"RItuicuo: {str(e)}")
            import traceback
            traceback.print_exc()
            self.status_label.setText(f'aiaaaa: {str(e)}')
        finally:
            self.is_requesting = False

    def on_daily_songs_received(self, song_list):
        self.song_list.clear()
        for song in song_list:
            self.song_list.addItem(f"{song.name}ID:{song.id}")

    def on_song_clicked(self, item):
        text = item.text()
        song_id = text.split("ID:")[-1]
        try:
            song_id = int(song_id)
            self.recommend_api.get_songs_url(song_id)
            self.status_label.setText(f'Wait... ID: {song_id} 的URL')
        except ValueError:
            self.status_label.setText('DIanjiba')

    def on_song_url_received(self, song_id: str, url: str):
        if url:
            self.status_label.setText(f'GotitURL {song_id}')
            print(f"播放器的URL: {url}")
            # 调用播放器控件的播放方法
            self.player_controls.player_service.play_url(url)
        else:
            self.status_label.setText(f'CAO的URL {song_id}')
