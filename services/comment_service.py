import requests
from urllib.parse import urljoin
from typing import Optional


class CommentService:
    BASE_URL = "http://121.36.9.139:3000"

    def get_comments(self,
                     id: int,
                     type: int = 0,
                     page_no: int = 1,
                     page_size: int = 20,
                     sort_type: int = 3,
                     cursor: Optional[int] = None) -> dict:

        url = urljoin(self.BASE_URL, "comment/new")
        params = {
            "id": id,
            "type": type,
            "pageNo": page_no,
            "pageSize": page_size,
            "sortType": sort_type
        }

        if cursor and sort_type == 3 and page_no > 1:
            params["cursor"] = cursor

        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()