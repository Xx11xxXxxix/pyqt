from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget

from services.fm_service import FMService
from services.recommend_songs import RecommendAPI


class FMWindow(QWidget):
    song_url_received=pyqtSignal(str,str)
    def __init__(self,cookies):
        super().__init__()
        self.cookies=cookies
        self.fm_service=FMService()
        self.fm_service.set_cookies(cookies)
        self.recommend_api=RecommendAPI().instance()
        self.played_songs=[]
        self.current_song=None
        self.init_ui()
        self.get_next_song()

    def init_ui(self):
        layout=QVBoxLayout(self)

        self.next_btn=QPushButton('Next song')
        self.next_btn.clicked.connect(self.get_next_song)

        self.song_info_label=QLabel()

        self.history_list=QListWidget()
        self.history_list.setMaximumHeight(200)

        layout.addWidget(self.song_info_label)
        layout.addWidget(self.next_btn)
        layout.addWidget(QLabel("RECENT_PLAY"))
        layout.addWidget(self.history_list)

    def get_next_song(self):
        try:
            current_id=self.current_song['id'] if self.current_song else None
            response=self.fm_service.get_personal_fm(current_id)

            print(response)
            if response['code']==200 and response.get('data'):
                song=response['data'][0]
                self.current_song={
                    'id':song['id'],
                    'name':song['name'],
                    'artists':'/'.join(artist['name']for artist in song.get('artists',[]))
                }
                self.update_song_info()
                self.recommend_api.get_songs_url(song['id'])
                self.add_to_history(self.current_song)

        except Exception as e:
            print(f"WRONG_FM_SONG:{e}")
    def update_song_info(self):
        if self.current_song:
            self.song_info_label.setText(
                f"NOW_PLAYING:{self.current_song['name']}-{self.current_song['artists']}"
            )
    def add_to_history(self,song):
        if song not in self.played_songs:
            self.played_songs.append(song)
            if len(self.played_songs)>10:
                self.played_songs.pop(0)
            self.update_history_list()
    def update_history_list(self):
        self.history_list.clear()
        for song in reversed(self.played_songs):
            self.history_list.addItem(f"{song['name']}-{song['artists']}")
