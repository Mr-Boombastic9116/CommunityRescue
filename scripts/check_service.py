import sys
import socket
import urllib.request
import json
import subprocess

def check_port(host: str, port: int) -> bool:
    """Returns True if port is listening/in-use."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    result = s.connect_ex((host, port))
    s.close()
    return result == 0

def get_pid_on_port(port: int) -> int:
    """Finds the PID listening on the given port via netstat."""
    try:
        out = subprocess.check_output(f'netstat -ano -p tcp', shell=True).decode()
        for line in out.splitlines():
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.strip().split()
                if len(parts) >= 5:
                    return int(parts[-1])
    except Exception:
        pass
    return 0

def check_backend():
    is_busy = check_port('127.0.0.1', 5000)
    if not is_busy:
        print("FREE 5000 0")
        return 0

    pid = get_pid_on_port(5000)
    try:
        with urllib.request.urlopen('http://127.0.0.1:5000/api/health', timeout=1.5) as r:
            if r.status == 200:
                print(f"HEALTHY 5000 {pid}")
                return 0
    except Exception:
        pass

    print(f"CONFLICT 5000 {pid}")
    return 1

def check_frontend(port: int = 3000):
    is_busy = check_port('127.0.0.1', port)
    if not is_busy:
        print(f"FREE {port} 0")
        return 0

    pid = get_pid_on_port(port)
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/', timeout=1.5) as r:
            if r.status == 200:
                print(f"HEALTHY {port} {pid}")
                return 0
    except Exception:
        pass

    print(f"CONFLICT {port} {pid}")
    return 1

if __name__ == '__main__':
    target = sys.argv[1].lower() if len(sys.argv) > 1 else 'backend'
    if target == 'backend':
        check_backend()
    elif target == 'frontend':
        p = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
        check_frontend(p)

