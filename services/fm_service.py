from urllib.parse import urljoin

import requests


class FMService:
    BASE_URL = "http://121.36.9.139:3000"

    def __init__(self):
        self.cookies=None

    def set_cookies(self,cookies):
        self.cookies=cookies

    def get_personal_fm(self,current_song_id=None):
        base_endpoint="personal_fm"
        if current_song_id:
            base_endpoint=f"personal_fm/{current_song_id}"
        url = urljoin(self.BASE_URL,base_endpoint)
        headers={'Cookie': self.cookies}if self.cookies else{}
        response=requests.get(url,headers=headers)
        response.raise_for_status()
        return  response.json()



