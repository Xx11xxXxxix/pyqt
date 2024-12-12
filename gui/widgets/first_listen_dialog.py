import requests
from PyQt6.QtGui import QPixmap,QPalette
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox, QScrollArea, QWidget
from PyQt6.QtCore import Qt


class FirstListenDialog(QDialog):
    def __init__(self, data, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("你还记得吗")
        self.data=data or {}
        self.message=message or ""
        self.setGeometry(100, 100, 600, 800)
        self.song_info = self.data.get('songInfoDto', {})
        self.first_listen = self.data.get('musicFirstListenDto', {})
        self.total_play = self.data.get('musicTotalPlayDto', {})
        self.play_most = self.data.get('musicPlayMostDto', {}) or {}
        self.like_song = self.data.get('musicLikeSongDto', {}) or {}
        self.frequent_listen = self.data.get('musicFrequentListenDto', {}) or {}
        layout = QVBoxLayout()

        cover_url = data.get('songInfoDto', {}).get('coverUrl')
        if cover_url:
            try:
                image_label=QLabel()
                image_label.setFixedSize(200,200)
                image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                response=requests.get(cover_url)
                response.raise_for_status()
                pixmap=QPixmap()
                pixmap.loadFromData(response.content)
                scaled_pixmap=pixmap.scaled(
                    200,200,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                image_label.setPixmap(scaled_pixmap)
                layout.addWidget(image_label)
            except Exception as e:
                print(e)
        scroll_area=QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget=QWidget()
        scroll_layout=QVBoxLayout(scroll_widget)



        title_label = QLabel(f"title: {data.get('title')}")
        message_label = QLabel(f"message: {message}")

        song_info = data.get('songInfoDto', {})
        # songId_label = QLabel(f"songId: {song_info.get('songId')}")
        # songName_label = QLabel(f"songName: {song_info.get('songName')}")
        # singer_label = QLabel(f"singer: {song_info.get('singer')}")
        # pubTime_label = QLabel(f"pubTime: {song_info.get('pubTime')}")
        # coverUrl_label = QLabel(f"coverUrl: {song_info.get('coverUrl')}")
        # type_label = QLabel(f"type: {song_info.get('type')}")
        song_info_label=QLabel(
            f"歌曲ID哟：{self.song_info.get('songId')}|"
            f"歌曲名称是：{self.song_info.get('songName')}|"
            f"歌手是：{self.song_info.get('singer')}|"
            f"发布时间是：{self.song_info.get('pubTime')}|"
            f"封面链接哦：{self.song_info.get('coverUrl')}|"
            f"类型为：{self.song_info.get('type')}|"
        )
        song_info_label.setWordWrap(True)

        first_listen = data.get('musicFirstListenDto', {})
        # date_label = QLabel(f"date: {first_listen.get('date')}")
        # season_label = QLabel(f"season: {first_listen.get('season')}")
        # period_label = QLabel(f"period: {first_listen.get('period')}")
        # time_label = QLabel(f"time: {first_listen.get('time')}")
        # mainTitle_label = QLabel(f"mainTitle: {first_listen.get('mainTitle')}")
        # subTitle_label = QLabel(f"subTitle: {first_listen.get('subTitle')}")
        # desc_label = QLabel(f"desc: {first_listen.get('desc')}")
        # meetDuration_label = QLabel(f"meetDuration: {first_listen.get('meetDuration')}")
        # meetDurationDesc_label = QLabel(f"meetDurationDesc: {first_listen.get('meetDurationDesc')}")
        # listenTime_label = QLabel(f"listenTime: {first_listen.get('listenTime')}")
        first_listen_label=QLabel(
            f"欧尼酱从什么时间开始听的呢：{self.first_listen.get('date')}|"
            f"季节是：{self.first_listen.get('season')}|"
            f"时期是：{self.first_listen.get('period')}|"
            f"时间是：{self.first_listen.get('time')}|"
            f"主标题为：{self.first_listen.get('mainTitle')}|"
            f"副标题为：{self.first_listen.get('subTitle')}|"
            f"描述是：{self.first_listen.get('desc')}|"
            f"见面时长为：{self.first_listen.get('meetDuration')}|"
            f"见面时长描述为：{self.first_listen.get('meetDurationDesc')}|"
            f"听歌时间是：{self.first_listen.get('listenTime')}|"

        )
        first_listen_label.setWordWrap(True)


        total_play = data.get('musicTotalPlayDto', {})
        # playCount_label = QLabel(f"playCount: {total_play.get('playCount')}")
        # duration_label = QLabel(f"duration: {total_play.get('duration')}")
        # text_label = QLabel(f"text: {total_play.get('text')}")
        # maxPlayTimes_label = QLabel(f"maxPlayTimes: {total_play.get('maxPlayTimes')}")
        total_play_label=QLabel(
            f"播放次数：{self.total_play.get('playCount')}|"
            f"总时长为：{self.total_play.get('duration')}|"
            f"文字内容是：{self.total_play.get('text')}|"
            f"最大播放次数为：{self.total_play.get('maxPlayTimes')}|"
        )
        total_play_label.setWordWrap(True)

        play_most = data.get('musicPlayMostDto', {})
        # play_date_label = QLabel(f"date: {play_most.get('date')}")
        # timestamp_label = QLabel(f"timestamp: {play_most.get('timestamp')}")
        # play_text_label = QLabel(f"text: {play_most.get('text')}")
        # mostPlayedCount_label = QLabel(f"mostPlayedCount: {play_most.get('mostPlayedCount')}")
        play_most_label = QLabel(
            f"欧尼在{self.play_most.get('date', 'N/A')}天听的：|" 
            f"为什么在{self.play_most.get('timestamp', 'N/A')}点听呢：|"
            f"原来欧尼是{self.play_most.get('text', 'N/A')}这样的人|"
            f"欧尼好厉害佑来了{self.play_most.get('mostPlayedCount', 'N/A')}次！|"
        )
        play_most_label.setWordWrap(True)


        like_song = data.get('musicLikeSongDto', {})
        # like_text_label = QLabel(f"text: {like_song.get('text')}")
        # like_label = QLabel(f"like: {like_song.get('like')}")
        # collect_label = QLabel(f"collect: {like_song.get('collect')}")
        # like_mainTitle_label = QLabel(f"mainTitle: {like_song.get('mainTitle')}")
        # like_subTitle_label = QLabel(f"subTitle: {like_song.get('subTitle')}")
        # like_desc_label = QLabel(f"desc: {like_song.get('desc')}")
        # redTime_label = QLabel(f"redTime: {like_song.get('redTime')}")
        # redDesc_label = QLabel(f"redDesc: {like_song.get('redDesc')}")
        # redTimeStamp_label = QLabel(f"redTimeStamp: {like_song.get('redTimeStamp')}")
        like_song_label = QLabel(
            f"文字内容是：{self.like_song.get('text')}|"
            f"喜欢数为：{self.like_song.get('like')}|"
            f"收藏数为：{self.like_song.get('collect')}|"
            f"主标题为：{self.like_song.get('mainTitle')}|"
            f"副标题为：{self.like_song.get('subTitle')}|"
            f"描述是：{self.like_song.get('desc')}|"
            f"红色时间为：{self.like_song.get('redTime')}|"
            f"红色描述为：{self.like_song.get('redDesc')}|"
            f"红色时间戳为：{self.like_song.get('redTimeStamp')}|"
        )
        like_song_label.setWordWrap(True)



        frequent_listen = data.get('musicFrequentListenDto', {})
        # describe_label = QLabel(f"describe: {frequent_listen.get('describe')}")
        # startTime_label = QLabel(f"startTime: {frequent_listen.get('startTime')}")
        # endTime_label = QLabel(f"endTime: {frequent_listen.get('endTime')}")
        # timeDesc_label = QLabel(f"timeDesc: {frequent_listen.get('timeDesc')}")
        frequent_listen_label = QLabel(
            f"来描述一下哦：{self.frequent_listen.get('describe')}|"
            f"开始时间是：{self.frequent_listen.get('startTime')}|"
            f"结束时间是：{self.frequent_listen.get('endTime')}|"
            f"时间描述为：{self.frequent_listen.get('timeDesc')}|"
        )
        frequent_listen_label.setWordWrap(True)

        scroll_layout.addWidget(title_label)
        scroll_layout.addWidget(message_label)
        layout.addWidget(QLabel("回忆来了哦:"))

        scroll_layout.addWidget(song_info_label)
        scroll_layout.addWidget(first_listen_label)
        scroll_layout.addWidget(total_play_label)
        scroll_layout.addWidget(play_most_label)
        scroll_layout.addWidget(like_song_label)
        scroll_layout.addWidget(frequent_listen_label)
        # layout.addWidget(songId_label)
        # layout.addWidget(songName_label)
        # layout.addWidget(singer_label)
        # layout.addWidget(pubTime_label)
        # layout.addWidget(coverUrl_label)
        # layout.addWidget(type_label)
        #
        # layout.addWidget(QLabel("musicFirstListenDto:"))
        # layout.addWidget(date_label)
        # layout.addWidget(season_label)
        # layout.addWidget(period_label)
        # layout.addWidget(time_label)
        # layout.addWidget(mainTitle_label)
        # layout.addWidget(subTitle_label)
        # layout.addWidget(desc_label)
        # layout.addWidget(meetDuration_label)
        # layout.addWidget(meetDurationDesc_label)
        # layout.addWidget(listenTime_label)
        #
        # layout.addWidget(QLabel("musicTotalPlayDto:"))
        # layout.addWidget(playCount_label)
        # layout.addWidget(duration_label)
        # layout.addWidget(text_label)
        # layout.addWidget(maxPlayTimes_label)
        #
        # layout.addWidget(QLabel("musicPlayMostDto:"))
        # layout.addWidget(play_date_label)
        # layout.addWidget(timestamp_label)
        # layout.addWidget(play_text_label)
        # layout.addWidget(mostPlayedCount_label)
        #
        # layout.addWidget(QLabel("musicLikeSongDto:"))
        # layout.addWidget(like_text_label)
        # layout.addWidget(like_label)
        # layout.addWidget(collect_label)
        # layout.addWidget(like_mainTitle_label)
        # layout.addWidget(like_subTitle_label)
        # layout.addWidget(like_desc_label)
        # layout.addWidget(redTime_label)
        # layout.addWidget(redDesc_label)
        # layout.addWidget(redTimeStamp_label)
        #
        # layout.addWidget(QLabel("musicFrequentListenDto:"))
        # layout.addWidget(describe_label)
        # layout.addWidget(startTime_label)
        # layout.addWidget(endTime_label)
        # layout.addWidget(timeDesc_label)
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)


        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout)


        self.setLayout(scroll_layout)
    def set_background_image(self,cover_url):
        try:
            response=requests.get(cover_url)
            response.raise_for_status()
            pixmap=QPixmap()
            if pixmap.loadFromData(response.content):
                scaled_pixmap=pixmap.scaled(
                    self.size(),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation
                )
                palette=self.palette()
                palette.setBrush(self.backgroundRole(),scaled_pixmap)
                self.setPalette(palette)
                self.setAutoFillBackground(True)
                print("YEAH_BACKGROUND")
            else:
                print("NO_BACKGROUND")
        except Exception as e:
            print(f"NO!:{e}")


