import os
import sys
import webbrowser
import threading
import time
import uvicorn

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

def open_browser(url):
    time.sleep(1.5)
    print(f"\n[RedLamp Demo] Dang mo trinh duyet tai: {url}")
    webbrowser.open(url)

def main():
    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}"
    print("=" * 70)
    print("  KHOI DONG REDLAMP TIME SERIES ANOMALY DETECTION DEMO")
    print(f"  URL: {url}")
    print("  Khong train lai - Su dung mo hinh pre-trained da luu trong pretrain/")
    print("  Toi uu hoa chay tren CPU voi PyTorch & FastAPI")
    print("=" * 70)

    # Open browser automatically in a separate thread
    threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    from backend.app import app
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    main()

