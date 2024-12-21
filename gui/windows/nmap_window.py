from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QLineEdit


class NMAPWindow(QWidget):
    nmap_go = pyqtSignal(str, str, str, str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("NMAP")
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Window)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.scan_by_ip_btn = QPushButton('干单个ip')
        self.scan_by_ip_btn.clicked.connect(self.scan_by_ip)

        self.stop_button=QPushButton("✋停✋止✋这✋场✋")
        self.stop_button.clicked.connect(self.on_stop_spoofing)

        self.scan_all_btn = QPushButton('干所有ip')
        self.scan_all_btn.clicked.connect(self.scan_all)

        self.ip_input = QLineEdit(self)
        self.ip_input.setPlaceholderText('哪个ip')

        self.target_mac_input = QLineEdit(self)
        self.target_mac_input.setPlaceholderText('哪个mac')

        self.own_mac_input = QLineEdit(self)
        self.own_mac_input.setPlaceholderText('你的mac')

        self.gateway_ip_input = QLineEdit(self)
        self.gateway_ip_input.setPlaceholderText('网关ip')

        self.network_segment_input = QLineEdit(self)
        self.network_segment_input.setPlaceholderText('网段')

        self.ip_mac_list = QListWidget()
        self.ip_mac_list.setMaximumHeight(200)

        layout.addWidget(self.scan_by_ip_btn)
        layout.addWidget(self.scan_all_btn)
        layout.addWidget(QLabel("RECENT_PLAY"))
        layout.addWidget(self.ip_input)
        layout.addWidget(self.target_mac_input)
        layout.addWidget(self.own_mac_input)
        layout.addWidget(self.gateway_ip_input)
        layout.addWidget(self.network_segment_input)
        layout.addWidget(self.ip_mac_list)
        layout.addWidget(self.stop_button)

    def scan_by_ip(self):
        ip_address = self.ip_input.text()
        target_mac = self.target_mac_input.text()
        own_mac = self.own_mac_input.text()
        gateway_ip = self.gateway_ip_input.text()
        network_segment = self.network_segment_input.text()

        if ip_address and target_mac and own_mac and gateway_ip and network_segment:
            self.nmap_go.emit('scan_by_ip', ip_address, target_mac, own_mac, gateway_ip, network_segment)
            self.ip_mac_list.addItem(f" 开始干IP: {ip_address}")
        else:
            self.ip_mac_list.addItem("没填全")
    def scan_all(self):
        target_mac = self.target_mac_input.text()
        own_mac = self.own_mac_input.text()
        gateway_ip = self.gateway_ip_input.text()
        network_segment = self.network_segment_input.text()

        if all([target_mac, own_mac, gateway_ip, network_segment]):
            self.nmap_go.emit('scan_all', '', target_mac, own_mac, gateway_ip, network_segment)

            self.ip_mac_list.addItem("扫全部中...")
        else:
            self.ip_mac_list.addItem("没填全")

    def display_scan_result(self, result):
        self.ip_mac_list.addItem(result)

    def on_stop_spoofing(self):
        self.nmap_go.emit("stop_spoofing", "", "", "", "", "")
        self.ip_mac_list.addItem("STOPPED")