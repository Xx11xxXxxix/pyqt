import subprocess
from PyQt6.QtWidgets import QMainWindow, QWidget,  QListWidget, QLabel, QPushButton, QMessageBox, \
  QGridLayout

from gui.widgets.rdp_dialog import RDPDialog
from gui.windows.search_window import SearchWindow
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

        self.BASE_URL = "http://121.36.9.139:3000"
        self.init_ui()
        self.check_remote_control_status()
        self.recommend_api.daily_songs_received.connect(self.on_daily_songs_received)
        self.recommend_api.song_url_received.connect(self.on_song_url_received)
        self.is_requesting = False

        self.search_window.song_clicked.connect(self.play_song_by_id)

    def init_ui(self):
        self.setWindowTitle('已闻君，诸事安康。 遇佳人，不久婚嫁。 已闻君，得偿所想。 料得是，卿识君望')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        grid_layout=QGridLayout(central_widget)

        self.remote_control_btn = QPushButton('点我开远程')
        self.get_recommend_btn = QPushButton('不主动就是不喜欢了[多多捂脸]')
        self.rdp_btn = QPushButton('点我控人')
        self.search_window=SearchWindow(self.cookies)
        self.song_list=QListWidget()

        grid_layout.addWidget(self.remote_control_btn,0,0)
        grid_layout.addWidget(self.get_recommend_btn,1,0)
        grid_layout.addWidget(self.rdp_btn,2,0)
        grid_layout.addWidget(self.search_window,0,1)
        grid_layout.addWidget(self.song_list,1,1,2,2)


        self.remote_control_btn.clicked.connect(self.enable_remote_control)
        self.get_recommend_btn.clicked.connect(self.get_daily_songs)
        self.rdp_btn.clicked.connect(self.show_rdp_dialog)
        self.song_list.itemClicked.connect(self.on_song_clicked)


        self.player_controls = PlayerControls()
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

    def get_daily_songs(self):
        if self.is_requesting:
            print("卧槽重复请求了一会闪退")
            return

        try:
            self.is_requesting = True
            self.status_label.setText('...')
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

    def show_rdp_dialog(self):
        dialog = RDPDialog(self)
        dialog.exec()

    def play_song_by_id(self,song_id):
        try:
            self.recommend_api.get_songs_url(song_id)
            self.status_label.setText(f'wATTING........id:{song_id}')
        except Exception as e:
            self.status_label.setText('WRONG_PLAY_SONG')


