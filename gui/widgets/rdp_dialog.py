import os
import subprocess

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QComboBox)

from services.ip_servers import IPService
from services.rdp_service import RDPService
from services.wireguard_service import WireGuardService


class RDPDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rdp_service = RDPService()
        self.ip_service = IPService()
        self.wg_service = WireGuardService()
        self.init_ui()
        self.load_ip_list()

    def init_ui(self):
        self.setWindowTitle('填吧')
        layout = QVBoxLayout()

        ip_layout = QHBoxLayout()
        self.ip_combo = QComboBox()
        self.ip_combo.setEditable(True)
        ip_layout.addWidget(QLabel('你要控谁:'))
        ip_layout.addWidget(self.ip_combo)
        refresh_btn = QPushButton('刷新IP列表')
        refresh_btn.clicked.connect(self.load_ip_list)
        ip_layout.addWidget(refresh_btn)

        restart_btn = QPushButton('重启隧道')
        restart_btn.clicked.connect(self.restart_wg_service)
        ip_layout.addWidget(restart_btn)

        layout.addLayout(ip_layout)

        wg_layout = QHBoxLayout()
        setup_wg_btn = QPushButton('配置WireGuard')
        setup_wg_btn.clicked.connect(self.setup_wireguard)
        wg_layout.addWidget(setup_wg_btn)
        layout.addLayout(wg_layout)




        btn_layout = QHBoxLayout()
        save_btn = QPushButton('先保存再连')
        launch_btn = QPushButton('SENDIT!!!!!!!')

        save_btn.clicked.connect(self.save_rdp_config)
        launch_btn.clicked.connect(self.launch_rdp)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(launch_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)




    def launch_rdp(self):
        if not os.path.exists(self.rdp_service.rdp_path):
            QMessageBox.warning(self, '！！', '写配置啊先')
            return

        if self.rdp_service.launch_rdp():
            self.accept()
        else:
            QMessageBox.critical(self, '！！', '操了')

    def load_ip_list(self):
        try:
            ips = self.ip_service.get_active_ips()
            current_text = self.ip_combo.currentText()

            self.ip_combo.clear()
            self.ip_combo.addItems(ips)

            if current_text:
                self.ip_combo.setCurrentText(current_text)
            config_path = os.path.join(self.wg_service.wg_dir, "mine.conf")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config_lines = f.readlines()
                for i, line in enumerate(config_lines):
                    if line.strip().startswith('AllowedIPs'):
                        base_ips = "39.156.66.10/32, 39.105.172.46/32, 39.105.122.46/32, 192.168.1.103/32"
                        wg_ips = [f"{ip}/32" for ip in ips]
                        all_ips = f"{base_ips},{','.join(wg_ips)}"
                        config_lines[i] = f"AllowedIPs = {all_ips}\n"
                        break
                with open(config_path, 'w') as f:
                    f.writelines(config_lines)
        except Exception as e:
            QMessageBox.warning(self, '！！', f'IP列表错了看服务器防火墙去你ip地址多少: {str(e)}')

    def save_rdp_config(self):
        ip = self.ip_combo.currentText().strip()
        if not ip:
            QMessageBox.warning(self, '！！', '填啊')
            return

        if self.rdp_service.create_rdp_file(ip):
            QMessageBox.information(self, 'OK', '连吧')
        else:
            QMessageBox.critical(self, '！！', '保存错了')

    def setup_wireguard(self):
        try:
            QMessageBox.information(self, '....', '等着配置WireGuard...')
            public_key = self.wg_service.generate_keys()
            server_config = self.wg_service.get_server_config(public_key)
            if not server_config.get('success'):
                raise Exception(server_config.get('error', '服务器出错'))
            self.wg_service.create_config_file(
                server_config['ip'],
                server_config['server_public_key']
            )
            self.wg_service.install_service()
            QMessageBox.information(self, 'DONE', f'隧道配置好了\nIP: {server_config["ip"]}')
            self.load_ip_list()
        except Exception as e:
            QMessageBox.critical(self, '!!!', f'隧道配置坏了: {str(e)}')

    def restart_wg_service(self):
        try:
            self.wg_service.restart_service()
            QMessageBox.information(self, 'DONE', '隧道重启了')
        except Exception as e:
            QMessageBox.critical(self, '！！！', f'隧道没重启: {str(e)}')