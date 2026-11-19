import os
import sys
import subprocess
import shutil
import webbrowser
import threading
import time

# Tu dong phat hien va chuyen huong sang Python 3.12 neu moi truong hien tai thieu thu vien
def _ensure_correct_python():
    if os.environ.get("_REDLAMP_REEXEC") == "1":
        return
    try:
        import fastapi
        import uvicorn
        import torch
    except ImportError:
        candidates = []
        if shutil.which("py"):
            candidates.append(["py", "-3.12"])
        py312_paths = [
            os.path.expanduser(r"~\AppData\Local\Python\pythoncore-3.12-64\python.exe"),
            r"C:\Python312\python.exe",
            r"C:\Program Files\Python312\python.exe",
        ]
        for p in py312_paths:
            if os.path.exists(p):
                candidates.append([p])
        
        for base_cmd in candidates:
            cmd = base_cmd + [os.path.abspath(__file__)] + sys.argv[1:]
            os.environ["_REDLAMP_REEXEC"] = "1"
            print(f"[RedLamp Demo] Phat hien dang chay tren Python {sys.version.split()[0]} chua co du FastAPI/PyTorch.")
            print(f"[RedLamp Demo] Tu dong chuyen huong sang Python 3.12 ({' '.join(base_cmd)})...\n")
            try:
                ret = subprocess.run(cmd)
                sys.exit(ret.returncode)
            except Exception:
                continue

_ensure_correct_python()

import uvicorn

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DEMO_DIR = os.path.join(BASE_DIR, "redlamp_demo")
if DEMO_DIR not in sys.path:
    sys.path.insert(0, DEMO_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.chdir(DEMO_DIR)

def open_browser(url):
    time.sleep(1.5)
    print(f"\n[RedLamp Demo] Dang mo trinh duyet tai: {url}")
    webbrowser.open(url)

def get_available_port(host="127.0.0.1", default_port=8000):
    import socket
    import urllib.request
    # Kiem tra neu RedLamp Demo da dang chay san tren default_port
    try:
        with urllib.request.urlopen(f"http://{host}:{default_port}/api/index", timeout=1) as resp:
            if resp.status == 200:
                return default_port, True
    except Exception:
        pass

    # Tim port trong de khoi chay
    for p in range(default_port, default_port + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, p))
                return p, False
            except OSError:
                continue
    return default_port, False

def main():
    host = "127.0.0.1"
    port, already_running = get_available_port(host, 8000)
    url = f"http://{host}:{port}"

    if already_running:
        print("=" * 70)
        print("  REDLAMP DEMO SERVER DANG HOAT DONG SAN TAI:")
        print(f"  URL: {url}")
        print("=" * 70)
        open_browser(url)
        print("\nBan co the dong tien trinh server cu neu muon khoi dong lai.")
        return

    print("=" * 70)
    print("  KHOI DONG REDLAMP TIME SERIES ANOMALY DETECTION DEMO")
    print(f"  URL: {url}")
    print("  Chay tren CPU voi PyTorch & FastAPI (Giong 100% redlamp_demo)")
    print("=" * 70)

    # Open browser automatically in a separate thread
    threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    from server import app
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    main()
