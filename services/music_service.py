import requests
from urllib.parse import urljoin

class MusicService:
    BASE_URL="http://121.36.9.139:3000"


    def search_multimatch(self,keywords,cookies):
        url=urljoin(self.BASE_URL,"search/multimatch")
        params={
            "keywords":keywords,
            "cookie":cookies
        }

        response=requests.get(url,params=params)
        response.raise_for_status()
        print(response.text)
        return response.json()

    def search_all(self,keywords,limit=30,offset=0,type=1):
        url=urljoin(self.BASE_URL,"cloudsearch")
        params={
            "keywords":keywords,
            "limit":limit,
            "offset":offset,
            "type":type
        }
        response=requests.get(url,params=params)
        response.raise_for_status()
        return response.json()