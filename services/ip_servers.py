import requests


class IPService:
    def __init__(self):
        self.base_url = "http://121.36.9.139:1089"

    def get_active_ips(self):
        try:
            response = requests.get(f"{self.base_url}/active_ips")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('ips', [])
            return []
        except Exception as e:
            print(f"ip列表出错啦: {str(e)}")
            return []