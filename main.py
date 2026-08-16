from datetime import datetime, timezone
from fastapi import FastAPI

app = FastAPI(title="Server Time API")


@app.get("/")
def root():
    return {"status": "ok", "service": "server-time"}


@app.get("/time")
def get_server_time():
    now = datetime.now(timezone.utc)
    return {
        "iso": now.isoformat(),
        "epoch": int(now.timestamp()),
        "tz": "UTC"
    }
