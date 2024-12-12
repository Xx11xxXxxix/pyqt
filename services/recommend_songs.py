import json
from dataclasses import dataclass
import requests
from PyQt6.QtCore import QObject, pyqtSignal, QUrl, QUrlQuery
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply


@dataclass
class Song:
    name: str
    id: int


class RecommendAPI(QObject):
    daily_songs_received = pyqtSignal(list)
    song_url_received = pyqtSignal(str, str)
    _instance = None
    _cookies = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, parent=None):
        super().__init__(parent)
        self.network_manager = QNetworkAccessManager()
        self.BASE_URL = "http://121.36.9.139:3000"
        self.current_reply = None

    @classmethod
    def set_cookies(cls, cookies):
        cls._cookies = cookies


    def get_daily_songs(self):
        if not self._cookies:
            print("zhaocookiequ")
            return

        try:
            if self.current_reply:
                if self.current_reply.isRunning():
                    print("Aborting previous request")
                    self.current_reply.abort()
                self.current_reply.deleteLater()
                self.current_reply = None
        except Exception as e:
            print(f"Error cleaning up previous request: {e}")

        url = QUrl(f"{self.BASE_URL}/recommend/songs")
        query = QUrlQuery()
        query.addQueryItem("cookie", self._cookies)
        url.setQuery(query)

        request = QNetworkRequest(url)
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")

        # 创建新请求
        self.current_reply = self.network_manager.get(request)
        self.current_reply.finished.connect(self._handle_daily_songs_response)
        self.current_reply.errorOccurred.connect(self._handle_network_error)

    def _handle_network_error(self, error):
        print(f"Network error occurred: {error}")
        if self.current_reply:
            print(f"Error string: {self.current_reply.errorString()}")

    def _handle_daily_songs_response(self):
        print("Handling daily songs response")
        if not self.current_reply:
            print("No current reply object")
            return

        reply = self.current_reply

        try:
            if reply.error() != QNetworkReply.NetworkError.NoError:
                print(f"Network error: {reply.error()}")
                print(f"Error string: {reply.errorString()}")
                return

            response_data = bytes(reply.readAll()).decode('utf-8')
            print(f"Response received, length: {len(response_data)}")

            data = json.loads(response_data)
            if not data.get('data'):
                print("No data in response")
                return

            songs = data['data'].get('dailySongs', [])
            print(f"Found {len(songs)} songs")

            song_list = []
            for song_data in songs:
                song = Song(
                    name=song_data.get('name', ''),
                    id=song_data.get('id', 0)
                )
                song_list.append(song)

            print("Emitting daily_songs_received signal")
            self.daily_songs_received.emit(song_list)

        except Exception as e:
            print(f"Error in handle_daily_songs_response: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            try:
                reply.deleteLater()
                if reply == self.current_reply:
                    self.current_reply = None
            except Exception as e:
                print(f"山列表出错了: {e}")

    def get_songs_url(self, song_id: int):
        if not self._cookies:
            print("meicookie")
            return
        url = QUrl(f"{self.BASE_URL}/song/url")
        query = f"id={song_id}&cookie={self._cookies}"
        url.setQuery(query)
        request = QNetworkRequest(url)
        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self.handle_song_url_response(reply, song_id))

    def handle_song_url_response(self, reply: QNetworkReply, song_id: int):
        reply.deleteLater()
        if reply.error() == QNetworkReply.NetworkError.NoError:
            try:
                data = json.loads(bytes(reply.readAll()).decode())
                if data.get('code') == 200 and data.get('data'):
                    url_info = data['data'][0]
                    if url_info.get('url'):
                        self.song_url_received.emit(str(song_id), url_info['url'])
                    else:
                        print(f"meiurl: {song_id}")
                else:
                    print(f"APIcuokendingde: {data}")
            except Exception as e:
                print(f"Wanle: {e}")
        else:
            print(f"KaiNOdele?: {reply.error()}")