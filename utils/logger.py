
from datetime import datetime

def log(msg):
    with open("debug.log", "a", encoding="utf-8") as f:
        now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        f.write(f"[{now}] {msg}\n")
