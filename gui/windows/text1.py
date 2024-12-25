import ipaddress
import subprocess
import platform
import threading
from queue import Queue
import time
import re


class NetworkDiscovery:
    def __init__(self, network):
        """
        初始化网络发现工具
        network: 目标网络 (例如 '192.168.1.0/24')
        """
        self.network = ipaddress.ip_network(network)
        self.results = {}
        self.queue = Queue()
        self.lock = threading.Lock()

        # 确定操作系统的初始TTL值
        # Windows: 128
        # Linux: 64
        # macOS: 64
        self.initial_ttl = 128 if platform.system().lower() == 'windows' else 64

    def get_ttl_and_time(self, ip):
        """
        执行ping测试并获取TTL值和响应时间
        返回: (跳数, 响应时间ms)，如果无响应则返回None
        """
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', str(ip)]

        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)

            # 提取TTL值
            ttl_match = re.search(r'TTL=(\d+)', output, re.IGNORECASE)
            if not ttl_match:
                return None

            received_ttl = int(ttl_match.group(1))
            # 计算跳数 = 初始TTL - 收到的TTL
            hops = self.initial_ttl - received_ttl

            # 提取响应时间
            if platform.system().lower() == 'windows':
                time_match = re.search(r'时间=(\d+)ms', output)
            else:
                time_match = re.search(r'time=(\d+\.?\d*)', output)

            if not time_match:
                return None

            response_time = float(time_match.group(1))

            return (hops, response_time)
        except:
            return None

    def worker(self):
        """
        工作线程：从队列获取IP并执行ping测试
        """
        while True:
            ip = self.queue.get()
            if ip is None:
                break

            result = self.get_ttl_and_time(ip)
            if result is not None:
                with self.lock:
                    self.results[str(ip)] = result

            self.queue.task_done()

    def discover(self, num_threads=10):
        """
        开始网络发现过程
        num_threads: 并发线程数
        返回: 按跳数和响应时间排序的结果
        """
        # 创建工作线程
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=self.worker)
            t.start()
            threads.append(t)

        # 将IP地址加入队列
        for ip in self.network.hosts():
            self.queue.put(ip)

        # 添加结束标记
        for _ in range(num_threads):
            self.queue.put(None)

        # 等待所有线程完成
        for t in threads:
            t.join()

        # 首先按跳数排序，跳数相同则按响应时间排序
        sorted_results = sorted(self.results.items(), key=lambda x: (x[1][0], x[1][1]))
        return sorted_results


def main():
    try:
        network = input("请输入要扫描的网络 (例如 192.168.1.0/24): ")
        discoverer = NetworkDiscovery(network)
        print(f"开始扫描网络 {network}...")

        start_time = time.time()
        results = discoverer.discover()
        end_time = time.time()

        print(f"\n扫描完成! 用时: {end_time - start_time:.2f} 秒")
        print(f"发现 {len(results)} 个活动主机:\n")

        print("IP地址            跳数    响应时间(ms)")
        print("-" * 45)
        for ip, (hops, response_time) in results:
            print(f"{ip:<16} {hops:>4d}    {response_time:>8.2f}")

    except KeyboardInterrupt:
        print("\n扫描被用户中断")
    except Exception as e:
        print(f"\n发生错误: {e}")


if __name__ == "__main__":
    main()