import requests
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt

class FirstListenDialog(QDialog):
    def __init__(self, data, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("回忆信息")
        self.setGeometry(100, 100, 600, 800)
        layout = QVBoxLayout()

        cover_url = data.get('songInfoDto', {}).get('coverUrl')
        if cover_url:
            print(122112)
            try:
                response = requests.get(cover_url)
                response.raise_for_status()
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                palette = self.palette()
                palette.setBrush(self.backgroundRole(), pixmap)
                self.setPalette(palette)
                self.setAutoFillBackground(True)
            except:
                pass
##1
        title_label = QLabel(f"title: {data.get('title')}")
        message_label = QLabel(f"message: {message}")

        song_info = data.get('songInfoDto', {})
        songId_label = QLabel(f"songId: {song_info.get('songId')}")
        songName_label = QLabel(f"songName: {song_info.get('songName')}")
        singer_label = QLabel(f"singer: {song_info.get('singer')}")
        pubTime_label = QLabel(f"pubTime: {song_info.get('pubTime')}")
        coverUrl_label = QLabel(f"coverUrl: {song_info.get('coverUrl')}")
        type_label = QLabel(f"type: {song_info.get('type')}")

        first_listen = data.get('musicFirstListenDto', {})
        date_label = QLabel(f"date: {first_listen.get('date')}")
        season_label = QLabel(f"season: {first_listen.get('season')}")
        period_label = QLabel(f"period: {first_listen.get('period')}")
        time_label = QLabel(f"time: {first_listen.get('time')}")
        mainTitle_label = QLabel(f"mainTitle: {first_listen.get('mainTitle')}")
        subTitle_label = QLabel(f"subTitle: {first_listen.get('subTitle')}")
        desc_label = QLabel(f"desc: {first_listen.get('desc')}")
        meetDuration_label = QLabel(f"meetDuration: {first_listen.get('meetDuration')}")
        meetDurationDesc_label = QLabel(f"meetDurationDesc: {first_listen.get('meetDurationDesc')}")
        listenTime_label = QLabel(f"listenTime: {first_listen.get('listenTime')}")

        total_play = data.get('musicTotalPlayDto', {})
        playCount_label = QLabel(f"playCount: {total_play.get('playCount')}")
        duration_label = QLabel(f"duration: {total_play.get('duration')}")
        text_label = QLabel(f"text: {total_play.get('text')}")
        maxPlayTimes_label = QLabel(f"maxPlayTimes: {total_play.get('maxPlayTimes')}")

        play_most = data.get('musicPlayMostDto', {})
        play_date_label = QLabel(f"date: {play_most.get('date')}")
        timestamp_label = QLabel(f"timestamp: {play_most.get('timestamp')}")
        play_text_label = QLabel(f"text: {play_most.get('text')}")
        mostPlayedCount_label = QLabel(f"mostPlayedCount: {play_most.get('mostPlayedCount')}")

        like_song = data.get('musicLikeSongDto', {})
        like_text_label = QLabel(f"text: {like_song.get('text')}")
        like_label = QLabel(f"like: {like_song.get('like')}")
        collect_label = QLabel(f"collect: {like_song.get('collect')}")
        like_mainTitle_label = QLabel(f"mainTitle: {like_song.get('mainTitle')}")
        like_subTitle_label = QLabel(f"subTitle: {like_song.get('subTitle')}")
        like_desc_label = QLabel(f"desc: {like_song.get('desc')}")
        redTime_label = QLabel(f"redTime: {like_song.get('redTime')}")
        redDesc_label = QLabel(f"redDesc: {like_song.get('redDesc')}")
        redTimeStamp_label = QLabel(f"redTimeStamp: {like_song.get('redTimeStamp')}")

        frequent_listen = data.get('musicFrequentListenDto', {})
        describe_label = QLabel(f"describe: {frequent_listen.get('describe')}")
        startTime_label = QLabel(f"startTime: {frequent_listen.get('startTime')}")
        endTime_label = QLabel(f"endTime: {frequent_listen.get('endTime')}")
        timeDesc_label = QLabel(f"timeDesc: {frequent_listen.get('timeDesc')}")

        layout.addWidget(title_label)
        layout.addWidget(message_label)

        layout.addWidget(QLabel("songInfoDto:"))
        layout.addWidget(songId_label)
        layout.addWidget(songName_label)
        layout.addWidget(singer_label)
        layout.addWidget(pubTime_label)
        layout.addWidget(coverUrl_label)
        layout.addWidget(type_label)

        layout.addWidget(QLabel("musicFirstListenDto:"))
        layout.addWidget(date_label)
        layout.addWidget(season_label)
        layout.addWidget(period_label)
        layout.addWidget(time_label)
        layout.addWidget(mainTitle_label)
        layout.addWidget(subTitle_label)
        layout.addWidget(desc_label)
        layout.addWidget(meetDuration_label)
        layout.addWidget(meetDurationDesc_label)
        layout.addWidget(listenTime_label)

        layout.addWidget(QLabel("musicTotalPlayDto:"))
        layout.addWidget(playCount_label)
        layout.addWidget(duration_label)
        layout.addWidget(text_label)
        layout.addWidget(maxPlayTimes_label)

        layout.addWidget(QLabel("musicPlayMostDto:"))
        layout.addWidget(play_date_label)
        layout.addWidget(timestamp_label)
        layout.addWidget(play_text_label)
        layout.addWidget(mostPlayedCount_label)

        layout.addWidget(QLabel("musicLikeSongDto:"))
        layout.addWidget(like_text_label)
        layout.addWidget(like_label)
        layout.addWidget(collect_label)
        layout.addWidget(like_mainTitle_label)
        layout.addWidget(like_subTitle_label)
        layout.addWidget(like_desc_label)
        layout.addWidget(redTime_label)
        layout.addWidget(redDesc_label)
        layout.addWidget(redTimeStamp_label)

        layout.addWidget(QLabel("musicFrequentListenDto:"))
        layout.addWidget(describe_label)
        layout.addWidget(startTime_label)
        layout.addWidget(endTime_label)
        layout.addWidget(timeDesc_label)

        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout)