import os
import subprocess


class RDPService:
    def __init__(self):
        self.rdp_path = "./RDP/RDP.rdp"
        self.rdp_template = """screen mode id:i:1
use multimon:i:0
desktopwidth:i:1280
desktopheight:i:720
session bpp:i:15
winposstr:s:0,1,291,95,1587,854
compression:i:1
keyboardhook:i:2
audiocapturemode:i:0
videoplaybackmode:i:1
connection type:i:7
networkautodetect:i:1
bandwidthautodetect:i:1
displayconnectionbar:i:1
enableworkspacereconnect:i:0
disable wallpaper:i:0
allow font smoothing:i:0
allow desktop composition:i:0
disable full window drag:i:1
disable menu anims:i:1
disable themes:i:0
disable cursor setting:i:0
bitmapcachepersistenable:i:1
full address:s:{ip}
audiomode:i:0
redirectprinters:i:1
redirectcomports:i:0
redirectsmartcards:i:1
redirectwebauthn:i:1
redirectclipboard:i:1
redirectposdevices:i:0
autoreconnection enabled:i:1
authentication level:i:2
prompt for credentials:i:0
negotiate security layer:i:1
remoteapplicationmode:i:0
alternate shell:s:
shell working directory:s:
gatewayhostname:s:
gatewayusagemethod:i:4
gatewaycredentialssource:i:4
gatewayprofileusagemethod:i:0
promptcredentialonce:i:0
gatewaybrokeringtype:i:0
use redirection server name:i:0
rdgiskdcproxy:i:0
kdcproxyname:s:
enablerdsaadauth:i:0
drivestoredirect:s:"""

    def create_rdp_file(self, ip_address: str, filename: str = "./RDP/RDP.rdp") -> bool:
        try:
            rdp_content = self.rdp_template.format(ip=ip_address)
            with open(filename, 'w') as f:
                f.write(rdp_content)
            return True
        except Exception as e:
            print(f"RDP文件创建时报错: {str(e)}")
            return False

    def launch_rdp(self) -> bool:
        try:
            if not os.path.exists(self.rdp_path):
                return False
            command = f'mstsc "{os.path.abspath(self.rdp_path)}"'
            subprocess.Popen(command, shell=True)
            return True
        except Exception as e:
            print(f"控人出错: {str(e)}")
            return False
