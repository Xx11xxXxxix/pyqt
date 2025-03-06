# recommend_window.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from services.music_service import MusicService
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict

@dataclass
class Artist:
    id: int
    name: str
    aliases: List[str] = field(default_factory=list)
    alia: List[str] = field(default_factory=list)

@dataclass
class Album:
    id: int
    name: str
    picUrl: str
    pic_str: str
    pic: int

@dataclass
class Privilege:
    id: int
    fee: int
    payed: int
    st: int
    pl: int
    dl: int
    sp: int
    cp: int
    subp: int
    cs: bool
    maxbr: int
    fl: int
    toast: bool
    flag: int
    preSell: bool
    playMaxbr: int
    downloadMaxbr: int
    maxBrLevel: str
    playMaxBrLevel: str
    downloadMaxBrLevel: str
    plLevel: str
    dlLevel: str
    flLevel: str
    rscl: Optional[Any]
    freeTrialPrivilege: Dict[str, Any]
    rightSource: int
    chargeInfoList: List[Dict[str, Any]]

@dataclass
class Song:
    name: str
    id: int
    artists: List[Artist]
    alia: List[str]
    pop: int
    st: int
    rt: str
    fee: int
    version: int
    crbt: Optional[str]
    cf: str
    album: Album
    dt: int
    h: Dict[str, Any]
    m: Dict[str, Any]
    l: Dict[str, Any]
    sq: Optional[Dict[str, Any]]
    hr: Optional[Dict[str, Any]]
    a: Optional[Any]
    cd: str
    no: int
    rtUrl: Optional[Any]
    ftype: int
    rtUrls: List[Any]
    djId: int
    copyright: int
    s_id: int
    mark: int
    originCoverType: int
    originSongSimpleData: Optional[Any]
    tagPicList: Optional[Any]
    resourceState: bool
    version: int
    songJumpInfo: Optional[Any]
    entertainmentTags: Optional[Any]
    single: int
    noCopyrightRcmd: Optional[Any]
    rtype: int
    rurl: Optional[Any]
    mst: int
    cp: int
    mv: int
    publishTime: int
    privilege: Privilege

class RecommendWindow(QWidget):
    track_songs=pyqtSignal(list)

    def __init__(self, cookies):
        super().__init__()
        self.cookies = cookies
        self.music_service = MusicService()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('今天有啥破歌单')
        self.setGeometry(150, 150, 800, 600)

        layout = QVBoxLayout()
        
        self.recommend_btn = QPushButton('你的破歌单')


        self.recommend_btn.clicked.connect(self.get_recommend_resource)

        self.result_table = QTableWidget()
        headers = ["名称", "ID", "创建者", "歌曲数量", "封面", "播放次数", "文案"]
        self.result_table.setColumnCount(len(headers))
        self.result_table.setHorizontalHeaderLabels(headers)
        self.result_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # 不让编辑
        self.result_table.cellClicked.connect(self.on_result_table_clicked)

        layout.addWidget(self.recommend_btn)
        layout.addWidget(self.result_table)

        self.setLayout(layout)

    def get_recommend_resource(self):
        try:
            results = self.music_service.get_recommend_resource(self.cookies)
            self.update_results_list(results)
        except Exception as e:
            QMessageBox.critical(self, 'NO!!', f'WRONG_RECOMMEND_RECOUCE: {e}')

    def on_result_table_clicked(self, row, column):
        if column != 1:
            return

        id_item = self.result_table.item(row, 1)
        if id_item:
            try:
                playlist_id = int(id_item.text())
                self.fetch_playlist_tracks(playlist_id)
            except ValueError:
                QMessageBox.warning(self, 'NO!!', 'WRONG_TRACK_ID')
    def fetch_playlist_tracks(self,playlist_id):
        try:
            playlist_track_count_item=self.result_table.item(self.result_table.currentRow(),3)
            playlist_track_count=int(playlist_track_count_item.text()) if playlist_track_count_item and playlist_track_count_item.text() else None

            results=self.music_service.get_playlist_tracks(
                playlist_id=playlist_id,
                limit=20,
                offset=0,
                cookies=self.cookies
            )
            self.process_playlist_tracks(results)
        except Exception as e:
            QMessageBox.critical(self,'NO!',f'WRONG_RECOMMEND_track_id: {e}')

    def process_playlist_tracks(self, results):
        if results.get('code') == 200 and 'songs' in results:
            tracks = results['songs']
            songs = []
            for track in tracks:
                duration_ms = track.get('dt', 0)
                minutes = duration_ms // 60000
                seconds = (duration_ms % 60000) // 1000
                duration_str = f"{minutes:02d}:{seconds:02d}"
                fee = track.get('fee', 0)
                if fee == 1:
                    fee_str = "ONLY_VIP"
                elif fee == 0:
                    fee_str = "FREE"
                else:
                    fee_str = "PAID"
                has_sq = 'YEAH' if track.get('sq') else 'NO'
                has_hq = 'YEAH' if track.get('h') else 'NO'
                has_hr = 'YEAH' if track.get('hr') else 'NO'
                has_mv = 'YEAH' if track.get('mv') else 'NO'
                publish_timestamp = track.get('publishTime', 0)
                try:
                    from datetime import datetime
                    publish_time = datetime.fromtimestamp(publish_timestamp / 1000).strftime('%Y-%m-%d')
                except:
                    publish_time = str(publish_timestamp)
                song = {
                    'name': track.get('name', ''),
                    'id': track.get('id', 0),
                    'artists': '/'.join([artist.get('name', '') for artist in track.get('ar', [])]),
                    'album': track.get('al', {}).get('name', ''),
                    'album_picUrl': track.get('al', {}).get('picUrl', ''),
                    'dt': duration_str,
                    'fee_str': fee_str,
                    'has_sq': has_sq,
                    'has_hq': has_hq,
                    'has_hr': has_hr,
                    'has_mv': has_mv,
                    'pop': track.get('pop', 0),
                    'publishTime': publish_time,
                    'copyright': track.get('copyright', 0),
                    'version': track.get('version', 0)
                }
                songs.append(song)
            self.track_songs.emit(songs)
        else:
            QMessageBox.warning(self, 'NO!', 'WRONG_RECOMMEND_track_SONGS。')


    def update_results_list(self, results):
        self.result_table.clearContents()
        if results.get('code') == 200 and 'recommend' in results:
            playlists_data = results['recommend']
            self.result_table.setRowCount(len(playlists_data))

            for row, playlist_data in enumerate(playlists_data):
                name = playlist_data.get('name', '')
                id_ = playlist_data.get('id', 0)
                creator = playlist_data.get('creator', {})
                creator_nickname = creator.get('nickname', '')
                track_count = playlist_data.get('trackCount', 0)
                pic_url = playlist_data.get('picUrl', '')
                playcount = playlist_data.get('playcount', 0)
                copywriter = playlist_data.get('copywriter', '')

                self.result_table.setItem(row, 0, QTableWidgetItem(name))
                self.result_table.setItem(row, 1, QTableWidgetItem(str(id_)))
                self.result_table.setItem(row, 2, QTableWidgetItem(creator_nickname))
                self.result_table.setItem(row, 3, QTableWidgetItem(str(track_count)))
                self.result_table.setItem(row, 4, QTableWidgetItem(pic_url))
                self.result_table.setItem(row, 5, QTableWidgetItem(str(playcount)))
                self.result_table.setItem(row, 6, QTableWidgetItem(copywriter))

            self.result_table.resizeColumnsToContents()
        else:

            self.result_table.setRowCount(0)
            self.result_table.setColumnCount(1)
            self.result_table.setHorizontalHeaderLabels(["信息"])
            self.result_table.setItem(0, 0, QTableWidgetItem("NO"))

