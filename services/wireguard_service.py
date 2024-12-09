import os
import subprocess
import requests
import json


class WireGuardService:
    def __init__(self):
        self.wg_dir = os.path.abspath("./RDP/WireGuard")
        self.private_key_path = os.path.join(self.wg_dir, "private.key")
        self.public_key_path = os.path.join(self.wg_dir, "public.key")
        self.config_path = os.path.join(self.wg_dir, "mine.conf")
        self.wg_exe = os.path.join(self.wg_dir, "wg.exe")
        self.wireguard_exe = os.path.join(self.wg_dir, "wireguard.exe")
        self.server_url = "http://121.36.9.139:1089/add_peer"

    def generate_keys(self):
        try:
            os.makedirs(self.wg_dir, exist_ok=True)
            private_key = subprocess.check_output(
                [self.wg_exe, "genkey"],
                text=True
            ).strip()
            with open(self.private_key_path, 'w') as f:
                f.write(private_key)
            public_key = subprocess.check_output(
                [self.wg_exe, "pubkey"],
                input=private_key,
                text=True
            ).strip()
            with open(self.public_key_path, 'w') as f:
                f.write(public_key)
            return public_key
        except Exception as e:
            print(f"密钥生成报错啦: {str(e)}")
            raise

    def get_server_config(self, public_key):
        try:
            response = requests.post(
                self.server_url,
                json={'public_key': public_key},
                headers={'Content-Type': 'application/json'}
            )
            return response.json()
        except Exception as e:
            print(f"服务器没饭吗？？: {str(e)}")
            raise

    def create_config_file(self, assigned_ip, server_public_key):
        try:
            with open(self.private_key_path, 'r') as f:
                private_key = f.read().strip()

            config_content = f"""[Interface]
PrivateKey = {private_key}
Address = {assigned_ip}/32
DNS = 8.8.8.8

[Peer]
PublicKey = {server_public_key}
Endpoint = 121.36.9.139:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25"""

            with open(self.config_path, 'w') as f:
                f.write(config_content)

        except Exception as e:
            print(f"配置文件又几把咋了: {str(e)}")
            raise

    def install_service(self):
        """安装WireGuard服务"""
        try:
            config_path_abs = os.path.abspath(self.config_path)
            command = f'"{self.wireguard_exe}" /installtunnelservice "{config_path_abs}"'
            print(f"傻逼cmd: {command}")
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            print(f"这是cmd: {result.stdout}")
            if result.stderr:
                print(f"唉cmd: {result.stderr}")

            return True

        except Exception as e:
            print(f"服务器又炸了: {str(e)}")
            raise