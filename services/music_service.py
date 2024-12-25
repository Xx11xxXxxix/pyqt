from typing import Dict

import requests
from urllib.parse import urljoin

from services.http_client import AsyncHttpClient


class MusicService:
    def __init__(self):
        self.http_client=AsyncHttpClient.instance()

    BASE_URL="http://121.36.9.139:3000"


    async def search_multimatch(self,keywords,cookies)->Dict[str, any]:
        print(211212)
        return await self.http_client.get(
            "/search/multimatch",
            params={"keywords":keywords},
            cookies=cookies
        )
        # url=urljoin(self.BASE_URL,"search/multimatch")
        # params={
        #     "keywords":keywords,
        #     "cookie":cookies
        # }
        #
        # response=requests.get(url,params=params)
        # response.raise_for_status()
        # print(response.text)
        # return response.json()

    async def search_all(self,keywords,limit=30,offset=0,type=1)->Dict[str, any]:
        return await self.http_client.get(
            "/search/all",
            params={"keywords":keywords
                    ,"limit":limit
                    ,"offset":offset
                    ,"type":type},
        )
        # url=urljoin(self.BASE_URL,"cloudsearch")
        # params={
        #     "keywords":keywords,
        #     "limit":limit,
        #     "offset":offset,
        #     "type":type
        # }
        # response=requests.get(url,params=params)
        # response.raise_for_status()
        # return response.json()

    def get_recommend_resource(self, cookies):
        url = f"{self.BASE_URL}/recommend/resource"
        params = {
            'Cookie': cookies
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_playlist_tracks(self, playlist_id, limit=None, offset=0, cookies=None):
        url = f"{self.BASE_URL}/playlist/track/all"
        params = {
            'id': playlist_id,
            'offset': offset
        }
        if limit is not None:
            params['limit'] = limit

        headers = {}
        if cookies:
            headers['Cookie'] = cookies
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_recommend_songs_daily(self,cookies):
        url=f"{self.BASE_URL}/recommend/songs"
        params={
            'cookie':cookies
        }
        response=requests.get(url,params=params)
        response.raise_for_status()
        return response.json()
