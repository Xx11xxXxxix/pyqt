import requests
from urllib.parse import urljoin


class FirstListenService:
    BASE_URL = "http://121.36.9.139:3000"

    def get_first_listen_info(self, song_id, cookies=None):
        url = urljoin(self.BASE_URL, "/music/first/listen/info")
        params = {
            'id': song_id
        }

        headers = {}
        if cookies:
            headers['Cookie'] = cookies

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()