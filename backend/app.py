import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEMO_DIR = os.path.join(BASE_DIR, "redlamp_demo")
if DEMO_DIR not in sys.path:
    sys.path.insert(0, DEMO_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from server import app, indexer, engine

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
