import json
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path("logs/requests.jsonl")
LOG_PATH.parent.mkdir(exist_ok=True)

def log_request(payload: dict):
    payload["timestamp"] = datetime.now(timezone.utc).isoformat(timespec='milliseconds')
    
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(payload) + "\n")
        f.flush()