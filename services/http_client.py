from typing import Optional, Any, Dict

import aiohttp


class AsyncHttpClient:
    _instance=None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance=cls()
        return cls._instance

    def __init__(self):
        self.base_url="http://121.36.9.139:3000"
        self.session=None

    async def ensure_session(self):
        if self.session is None:
            self.session=aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()
            self.session=None

    async def request(self,
                      method:str,
                      endpoint:str,
                      params:Optional[Dict] = None,
                      cookies:Optional[str]=None,
                      **kwargs)->Dict[str,Any]:
        await self.ensure_session()

        url=f"{self.base_url}{endpoint}"
        headers={}
        if cookies:
            headers['Cookie']=cookies

        async with self.session.request(method,url,params=params,headers=headers,**kwargs) as r:
            r.raise_for_status()
            return await r.json()
    async def get(self,endpoint:str,**kwargs)->Dict[str,Any]:
        return await self.request('GET',endpoint,**kwargs)
    async def post(self,endpoint:str,**kwargs)->Dict[str,Any]:
        return await self.request('POST',endpoint,**kwargs)