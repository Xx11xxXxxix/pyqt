from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QLineEdit


class NMAPWindow(QWidget):
    nmap_go=pyqtSignal(str,str)
    def __init__(self,cookies):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout=QVBoxLayout(self)

        self.scan_by_ip_btn=QPushButton('SCAN_BY_IP')
        self.scan_by_ip_btn.clicked.connect(self.scan_by_ip)

        self.scan_all_btn=QPushButton('SCAN_ALL')
        self.scan_all_btn.clicked.connect(self.scan_all)

        self.ip_input=QLineEdit(self)
        self.ip_input.setPlaceholderText('INPUT_IP')

        self.ip_mac_list=QListWidget()
        self.ip_mac_list.setMaximumHeight(200)

        layout.addWidget(self.scan_by_ip_btn)
        layout.addWidget(self.scan_by_ip_btn)
        layout.addWidget(self.scan_all_btn)
        layout.addWidget(QLabel("RECENT_PLAY"))
        layout.addWidget(self.ip_mac_list)

    def scan_by_ip(self):
        ip_address=self.ip_input.text()
        if ip_address:
            self.nmap_go.emit('scan_by_ip',ip_address)
            self.ip_mac_list.addItem(f"Scanning IP:{ip_address}")
            self.display_scan_result(f"Result:{ip_address}")
        else:
            self.ip_mac_list.addItem("NO_IP")

    def scan_all(self):
        self.nmap_go.emit('scan_all')
        self.ip_mac_list.addItem("Scanning")
        self.display_scan_result("Res")

    def display_scan_result(self,result):
        self.ip_mac_list.addItem(result)



