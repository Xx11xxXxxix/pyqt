from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QListWidget, QVBoxLayout, QDialog, QHBoxLayout, QLineEdit, QPushButton, QMessageBox


class IPManagerDialog(QDialog):
    def __init__(self,config_path,parent=None):
        super().__init__(parent)
        self.config_path=config_path
        self.init_ui()


    def init_ui(self):
        self.setWindowTitle('IP ADDING')
        layout=QVBoxLayout()

        self.ip_list=QListWidget()
        self.load_current_ips()
        layout.addWidget(QLabel('Nowips:'))
        layout.addWidget(self.ip_list)

        input_layout=QHBoxLayout()
        self.ip_input=QLineEdit()
        self.ip_input.setPlaceholderText('INPUT new ip')
        add_button =QPushButton('xieba')
        add_button.clicked.connect(self.add_ip)
        input_layout.addWidget(self.ip_input)
        input_layout.addWidget(add_button)
        layout.addLayout(input_layout)

        delete_button=QPushButton('DELETE?')
        delete_button.clicked.connect(self.delete_ip)
        layout.addWidget(delete_button)

        self.setLayout(layout)

    def load_current_ips(self):
        try:
            with open(self.config_path,'r') as f:
                content=f.read()
                for line in content.split('\n'):
                    if line.startswith('AllowedIPs'):
                        ips=line.split('=')[1].strip()
                        ip_list=[ip.strip() for ip in ips.split(',')]
                        self.ip_list.addItems(ip_list)
                        break
        except Exception as e:
            QMessageBox.warning(self,'No!',f'FILE not FOUND:{str(e)}')

    def add_ip(self):
        new_ip = self.ip_input.text().strip()
        if not new_ip:
            return

        if '/' not in new_ip:
            new_ip+='/32'
        if self.is_valid_ip(new_ip):
            existing_items=[self.ip_list.item(i).text()
                            for i in range(self.ip_list.count())]
            if new_ip not in existing_items:
                self.ip_list.addItem(new_ip)
                self.save_config()
                self.ip_input.clear()
            else:
                QMessageBox.warning(self,'TIP:','IP ALREADY EXIST')
        else:
            QMessageBox.warning(self,'TIP:','IP WRONG FORMAT')

    def delete_ip(self):
        current_item=self.ip_list.currentItem()
        if current_item:
            self.ip_list.takeItem(self.ip_list.row(current_item))
            self.save_config()

    def save_config(self):
        try:
            with open (self.config_path,'r')as f:
                lines=f.readlines()
                new_ips=', '.join([self.ip_list.item(i).text()
                                   for i in range(self.ip_list.count())])
                with open(self.config_path,'w')as f:
                    for line in lines:
                        if line.startswith('AllowedIPs'):
                            f.write(f'AllowedIPs={new_ips}\n')
                        else:
                            f.write(line)
        except Exception as e:
            QMessageBox.warning(self,'NO!',f'SAVEING ERROR:{str(e)}')

    def is_valid_ip(self,ip):
        try:
            address,mask=ip.split('/')
            parts=address.split('.')
            return (len(parts)==4 and
                    all(0<int(part)<=255 for part in parts)and
                    0<=int(mask)<=32)
        except:
            return False