import subprocess
from PyQt6.QtWidgets import QMainWindow, QWidget, QListWidget, QLabel, QPushButton, QMessageBox, \
    QGridLayout, QTableWidgetItem

from gui.widgets.comment_widget import CommentWidget
from gui.widgets.rdp_dialog import RDPDialog
from gui.windows.fm_window import FMWindow
from gui.windows.nmap_window import NMAPWindow
from gui.windows.recommend_window import RecommendWindow
from gui.windows.search_window import SearchWindow
from services.recommend_songs import RecommendAPI
from gui.widgets.player_controls import PlayerControls, PlaylistWindow


class MainWindow(QMainWindow):
    def __init__(self, db_manager, user_id, cookies):
        super().__init__()
        self.db_manager = db_manager
        self.user_id = user_id
        self.cookies = cookies
        self.recommend_api = RecommendAPI.instance()
        self.recommend_api.set_cookies(cookies)

        self.BASE_URL = "http://121.36.9.139:3000"

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.init_ui()
        self.check_remote_control_status()
        self.recommend_api.song_url_received.connect(self.on_song_url_received)
        self.is_requesting = False

        self.search_window.song_clicked.connect(self.play_song_by_id)
        self.playlist_window=None



    def init_ui(self):
        grid_layout=QGridLayout(self.central_widget)

        self.player_controls = PlayerControls(self)



        self.setWindowTitle('已闻君，诸事安康。 遇佳人，不久婚嫁。 已闻君，得偿所想。 料得是，卿识君望')
        self.setGeometry(100, 100, 800, 600)

        self.nmap_button = QPushButton('Open NMAP Scanner')
        self.nmap_button.clicked.connect(self.open_nmap_window)

        self.remote_control_btn = QPushButton('点我开远程')
        self.rdp_btn = QPushButton('点我控人')
        self.search_window=SearchWindow(self.cookies)
        self.song_list=QListWidget()
        self.recommend_resource_btn = QPushButton('推荐歌单')
        self.comment_widget=CommentWidget()
        self.fm_button=QPushButton('FM')
        self.playlist_button=QPushButton("PLAY_LIST")



        grid_layout.addWidget(self.remote_control_btn,0,0)
        grid_layout.addWidget(self.rdp_btn,2,0)
        grid_layout.addWidget(self.search_window,0,1)
        grid_layout.addWidget(self.recommend_resource_btn,5,0)
        grid_layout.addWidget(self.comment_widget,1,1,2,2)
        grid_layout.addWidget(self.fm_button,6,0)
        grid_layout.addWidget(self.playlist_button,8,0)
        grid_layout.addWidget(self.nmap_button, 0, 0)


        self.remote_control_btn.clicked.connect(self.enable_remote_control)
        self.rdp_btn.clicked.connect(self.show_rdp_dialog)
        self.song_list.itemClicked.connect(self.on_song_clicked)
        self.recommend_resource_btn.clicked.connect(self.open_recommend_resource_window)
        self.search_window.add_to_playlist_signal.connect(self.on_add_to_playlist)
        self.fm_button.clicked.connect(self.open_fm_window)
        self.playlist_button.clicked.connect(self.show_playlist)


        self.status_label = QLabel('SENDIT!!!!!')

        grid_layout.addWidget(self.player_controls,3,0,1,3)
        grid_layout.addWidget(self.status_label,4,0,1,3)


    def check_remote_control_status(self):
        try:
            query_command = 'reg query "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections'
            result = subprocess.run(query_command, shell=True, capture_output=True, text=True)

            if result.returncode == 0 and "0x0" in result.stdout:
                self.remote_control_btn.setText('开了别几把点了')
                self.remote_control_btn.setEnabled(False)
        except Exception as e:
            print(f"检查远程错啦: {str(e)}")

    def enable_remote_control(self):
        try:
            command = 'reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f'
            result = subprocess.run(command, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                QMessageBox.information(self, '好了', '开了别几把点了')
                self.remote_control_btn.setText('开了别几把点了')
                self.remote_control_btn.setEnabled(False)
            else:
                QMessageBox.warning(self, '完了', f'完了: {result.stderr}')

        except Exception as e:
            QMessageBox.critical(self, '完了', f'完了: {str(e)}')



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
            if hasattr(self, 'comment_widget'):
                self.comment_widget.update_for_song(song_id)
            self.status_label.setText(f'GotitURL {song_id}')
            print(f"播放器的URL: {url}")
            self.player_controls.player_service.play_url(url)
        else:
            self.status_label.setText(f'CAO的URL {song_id}')

    def show_rdp_dialog(self):
        dialog = RDPDialog(self)
        dialog.exec()

    def play_song_by_id(self,song_id):
        try:
            self.recommend_api.get_songs_url(song_id)
            self.status_label.setText(f'wATTING........id:{song_id}')

        except Exception as e:
            self.status_label.setText('WRONG_PLAY_SONG')




    def on_song_clicked_from_search(self, song_id):
        try:
            self.recommend_api.get_songs_url(song_id)
            self.status_label.setText(f'WAITING......ID:{song_id}')
        except Exception as e:
            self.status_label.setText('WRONG_PLAYSONG')

    def open_recommend_resource_window(self):
        self.recommend_resource_window = RecommendWindow(self.cookies)
        self.recommend_resource_window.track_songs.connect(self.update_search_results)
        self.recommend_resource_window.show()


    def open_fm_window(self):
        self.fm_window=FMWindow(self.cookies)
        self.fm_window.show()

    def show_playlist(self):
        if self.playlist_window is None:
            self.playlist_window=PlaylistWindow(self)
        self.playlist_window.show()
        self.playlist_window.raise_()
        self.playlist_window.activateWindow()
    def on_add_to_playlist(self,song_info):
        self.player_controls.add_to_playlist(song_info)
        if self.playlist_window:
            self.playlist_window.add_song(song_info)

    def open_nmap_window(self):
        # Instantiate the NMAPWindow and show it
        self.nmap_window = NMAPWindow(self.cookies)
        self.nmap_window.show()










    def update_search_results(self, songs):
        self.search_window.result_table.clearContents()
        self.search_window.result_table.setColumnCount(len(self.search_window.search_headers))
        self.search_window.result_table.setHorizontalHeaderLabels(self.search_window.search_headers)
        self.search_window.result_table.setRowCount(len(songs))
        for row, song in enumerate(songs):
            self.search_window.result_table.setItem(row, 0, QTableWidgetItem(song['name']))
            self.search_window.result_table.setItem(row, 1, QTableWidgetItem(str(song['id'])))
            self.search_window.result_table.setItem(row, 2, QTableWidgetItem(song['artists']))
            self.search_window.result_table.setItem(row, 3, QTableWidgetItem(song['album']))
            self.search_window.result_table.setItem(row, 4, QTableWidgetItem(song['album_picUrl']))
            self.search_window.result_table.setItem(row, 5, QTableWidgetItem(song['dt']))
            self.search_window.result_table.setItem(row, 6, QTableWidgetItem(song['fee_str']))
            self.search_window.result_table.setItem(row, 7, QTableWidgetItem(song['has_sq']))
            self.search_window.result_table.setItem(row, 8, QTableWidgetItem(song['has_hq']))
            self.search_window.result_table.setItem(row, 9, QTableWidgetItem(song['has_hr']))
            self.search_window.result_table.setItem(row, 10, QTableWidgetItem(song['has_mv']))
            self.search_window.result_table.setItem(row, 11, QTableWidgetItem(str(song['pop'])))
            self.search_window.result_table.setItem(row, 12, QTableWidgetItem(song['publishTime']))
            self.search_window.result_table.setItem(row, 13, QTableWidgetItem(str(song['copyright'])))
            self.search_window.result_table.setItem(row, 14, QTableWidgetItem(str(song['version'])))
        self.search_window.result_table.resizeColumnsToContents()







