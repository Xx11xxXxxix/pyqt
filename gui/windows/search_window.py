from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QTableWidget,
                             QTableWidgetItem, QMessageBox, QPushButton)
from PyQt6.QtCore import QTimer, pyqtSignal, Qt

from gui.widgets.first_listen_dialog import FirstListenDialog
from gui.widgets.song_context_menu import SongContextMenu
from services.first_listen_service import  FirstListenService
from services.music_service import MusicService
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

class SearchWindow(QWidget):
    BASE_URL = "http://121.36.9.139:3000"
    song_clicked = pyqtSignal(int)

    def __init__(self, cookies):
        super().__init__()
        self.cookies=cookies
        self.music_service=MusicService()
        self.first_listen_service = FirstListenService()
        self.song_ids={}
        self.init_ui()


        self.search_timer=QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)

    def init_ui(self):
        layout = QVBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("SEARCH")

        self.result_table = QTableWidget()
        self.search_headers = ["歌曲", "ID", "艺术家", "专辑", "专辑封面", "时长", "收费类型", "无损音质", "高品质", "高清音质",
                   "MV", "热门度", "发行时间", "版权", "版本"]
        self.daily_headers = ["歌曲", "ID", "艺术家", "专辑", "专辑封面", "时长", "收费类型", "无损音质", "高品质",
                              "高清音质",
                              "MV", "热门度", "发行时间", "版权", "版本", "推荐原因", "推荐说明", "播放频率"]

        self.result_table.setColumnCount(len(self.search_headers))
        self.result_table.setHorizontalHeaderLabels(self.search_headers)
        self.recommend_songs_daily_btn = QPushButton('看你的破日推')
        self.result_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)


        self.recommend_songs_daily_btn.clicked.connect(self.recommend_songs_daily)
        self.result_table.cellClicked.connect(self.on_result_table_clicked)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.result_table.customContextMenuRequested.connect(self.show_context_menu)


        layout.addWidget(self.recommend_songs_daily_btn)
        layout.addWidget(self.search_input)
        layout.addWidget(self.result_table)

        self.setLayout(layout)

    def on_search_text_changed(self,text):
        self.search_timer.stop()
        if text:
            self.search_timer.start(500)

    def perform_search(self):
        keyword=self.search_input.text().strip()
        if not keyword:
            self.result_table.clearContents()
            self.result_table.setRowCount(0)
            return

        try:
            results=self.music_service.search_all(keyword,type=1)
            self.update_results_list(results)
        except Exception as e:
            print(f"SEARCH_WRONG:{e}")
            self.result_table.setRowCount(0)
            self.result_table.setColumnCount(1)
            self.result_table.setHorizontalHeaderLabels(["WHAT?"])
            self.result_table.setItem(0, 0, QTableWidgetItem("SEARCH_TABLE_WRONG"))


    def on_result_table_clicked(self, row, column):
        id_item = self.result_table.item(row, 1)
        if id_item:
            try:
                song_id = int(id_item.text())
                self.song_clicked.emit(song_id)
            except ValueError:
                print('WRONG Song ID')
    def recommend_songs_daily(self):
        try:
            results=self.music_service.get_recommend_songs_daily(self.cookies)
            if results.get('code') == 200 and 'data' in results and 'dailySongs' in results['data']:
                self.update_results_list(results)
            else:
                QMessageBox.warning(self,"NO!","WRONG_IN_recommend_songs_daily")
        except Exception as e:
            QMessageBox.critical(self,'NO!',f'WRONG_IN_recommend_songs_daily:{e}')
    def show_context_menu(self, position):
        row = self.result_table.rowAt(position.y())
        if row >= 0:
            id_item = self.result_table.item(row, 1)
            if id_item:
                try:
                    song_id = int(id_item.text())
                    menu = SongContextMenu(song_id, self)
                    menu.show_first_listen_info.connect(self.handle_first_listen_info)
                    menu.exec(self.result_table.viewport().mapToGlobal(position))
                except ValueError:
                    pass

    def handle_first_listen_info(self, song_id):
        try:
            result = self.first_listen_service.get_first_listen_info(song_id, self.cookies)
            full_data = result.get('data', {})
            message = result.get('message', '')
            print(result)
            if full_data:
                dialog = FirstListenDialog(full_data, message, self)
                dialog.exec()
            else:
                QMessageBox.information(self, "提示", "没有相关的听歌记录")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"获取听歌信息失败: {e}")





















    def update_results_list(self, results):
        self.result_table.clearContents()
        if 'result' in results and 'songs' in results['result']:
            songs_data = results['result']['songs']
            self.result_table.setColumnCount(len(self.search_headers))
            self.result_table.setHorizontalHeaderLabels(self.search_headers)
        elif 'data' in results and 'dailySongs' in results['data']:
            songs_data=results['data']['dailySongs']
            self.result_table.setColumnCount(len(self.daily_headers))
            self.result_table.setHorizontalHeaderLabels(self.daily_headers)
        else:
            self.result_table.setRowCount(0)
            self.result_table.setColumnCount(1)
            self.result_table.setHorizontalHeaderLabels(["INFO!!"])
            self.result_table.setItem(0,0,QTableWidgetItem("NO!"))
            return

        self.result_table.setRowCount(len(songs_data))

        for row, song_data in enumerate(songs_data):
            artists = [Artist(id=artist.get('id', 0),
                              name=artist.get('name', ''),
                              aliases=artist.get('alias', []),
                              alia=artist.get('alia', [])) for artist in song_data.get('ar', [])]
            artists_names = '/'.join([artist.name for artist in artists])

            al = song_data.get('al', {})
            album = Album(id=al.get('id', 0),
                          name=al.get('name', ''),
                          picUrl=al.get('picUrl', ''),
                          pic_str=al.get('pic_str', ''),
                          pic=al.get('pic', 0))

            priv = song_data.get('privilege', {})
            privilege = Privilege(
                id=priv.get('id', 0),
                fee=priv.get('fee', 0),
                payed=priv.get('payed', 0),
                st=priv.get('st', 0),
                pl=priv.get('pl', 0),
                dl=priv.get('dl', 0),
                sp=priv.get('sp', 0),
                cp=priv.get('cp', 0),
                subp=priv.get('subp', 0),
                cs=priv.get('cs', False),
                maxbr=priv.get('maxbr', 0),
                fl=priv.get('fl', 0),
                toast=priv.get('toast', False),
                flag=priv.get('flag', 0),
                preSell=priv.get('preSell', False),
                playMaxbr=priv.get('playMaxbr', 0),
                downloadMaxbr=priv.get('downloadMaxbr', 0),
                maxBrLevel=priv.get('maxBrLevel', ''),
                playMaxBrLevel=priv.get('playMaxBrLevel', ''),
                downloadMaxBrLevel=priv.get('downloadMaxBrLevel', ''),
                plLevel=priv.get('plLevel', ''),
                dlLevel=priv.get('dlLevel', ''),
                flLevel=priv.get('flLevel', ''),
                rscl=priv.get('rscl'),
                freeTrialPrivilege=priv.get('freeTrialPrivilege', {}),
                rightSource=priv.get('rightSource', 0),
                chargeInfoList=priv.get('chargeInfoList', [])
            )

            song = Song(
                name=song_data.get('name', ''),
                id=song_data.get('id', 0),
                artists=artists,
                alia=song_data.get('alia', []),
                pop=song_data.get('pop', 0),
                st=song_data.get('st', 0),
                rt=song_data.get('rt', ''),
                fee=song_data.get('fee', 0),
                version=song_data.get('v', 0),
                crbt=song_data.get('crbt'),
                cf=song_data.get('cf', ''),
                album=album,
                dt=song_data.get('dt', 0),
                h=song_data.get('h', {}),
                m=song_data.get('m', {}),
                l=song_data.get('l', {}),
                sq=song_data.get('sq'),
                hr=song_data.get('hr'),
                a=song_data.get('a'),
                cd=song_data.get('cd', ''),
                no=song_data.get('no', 0),
                rtUrl=song_data.get('rtUrl'),
                ftype=song_data.get('ftype', 0),
                rtUrls=song_data.get('rtUrls', []),
                djId=song_data.get('djId', 0),
                copyright=song_data.get('copyright', 0),
                s_id=song_data.get('s_id', 0),
                mark=song_data.get('mark', 0),
                originCoverType=song_data.get('originCoverType', 0),
                originSongSimpleData=song_data.get('originSongSimpleData'),
                tagPicList=song_data.get('tagPicList'),
                resourceState=song_data.get('resourceState', False),
                songJumpInfo=song_data.get('songJumpInfo'),
                entertainmentTags=song_data.get('entertainmentTags'),
                single=song_data.get('single', 0),
                noCopyrightRcmd=song_data.get('noCopyrightRcmd'),
                rtype=song_data.get('rtype', 0),
                rurl=song_data.get('rurl'),
                mst=song_data.get('mst', 0),
                cp=song_data.get('cp', 0),
                mv=song_data.get('mv', 0),
                publishTime=song_data.get('publishTime', 0),
                privilege=privilege
            )

            duration_sec = song.dt // 1000
            minutes = duration_sec // 60
            seconds = duration_sec % 60

            fee = song.fee
            if fee == 1:
                fee_str = "ONLY_VIP"
            elif fee == 0:
                fee_str = "FREE"
            else:
                fee_str = "PAID"

            has_sq = 'YEAH' if song.sq else 'NO'
            has_hq = 'YEAH' if song.h else "NO"
            has_hr = 'YEAH' if song.hr else "NO"
            has_mv = 'YEAH' if song.mv else "NO"

            self.result_table.setItem(row, 0, QTableWidgetItem(song.name))
            self.result_table.setItem(row, 1, QTableWidgetItem(str(song.id)))
            self.result_table.setItem(row, 2, QTableWidgetItem(artists_names))
            self.result_table.setItem(row, 3, QTableWidgetItem(song.album.name))
            self.result_table.setItem(row, 4, QTableWidgetItem(song.album.picUrl))
            self.result_table.setItem(row, 5, QTableWidgetItem(f"{minutes:02d}:{seconds:02d}"))
            self.result_table.setItem(row, 6, QTableWidgetItem(fee_str))
            self.result_table.setItem(row, 7, QTableWidgetItem(has_sq))
            self.result_table.setItem(row, 8, QTableWidgetItem(has_hq))
            self.result_table.setItem(row, 9, QTableWidgetItem(has_hr))
            self.result_table.setItem(row, 10, QTableWidgetItem(has_mv))
            self.result_table.setItem(row, 11, QTableWidgetItem(str(song.pop)))
            self.result_table.setItem(row, 12, QTableWidgetItem(str(song.publishTime)))
            self.result_table.setItem(row, 13, QTableWidgetItem(str(song.copyright)))
            self.result_table.setItem(row, 14, QTableWidgetItem(str(song.version)))
            if 'data' in results and 'dailySongs' in results['data']:
                self.result_table.setItem(row,15,QTableWidgetItem(song_data.get('reason','')))
                self.result_table.setItem(row,16,QTableWidgetItem(song_data.get('recommendReason','')))
                alg=song_data.get('alg','')
                self.result_table.setItem(row,17,QTableWidgetItem(alg))

