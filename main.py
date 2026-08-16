from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, Query

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


@app.get("/date")
def get_date(
    tz: str = Query("UTC", description="Часовой пояс, например UTC или Asia/Astrakhan"),
    fmt: str = Query("iso", description="Формат: iso, epoch, date, time, human"),
):
    try:
        offset = _parse_tz(tz)
    except ValueError as e:
        return {"error": str(e)}
    now = datetime.now(timezone.utc) + offset
    return _format(now, fmt, tz)


@app.get("/date/today")
def get_today(tz: str = Query("UTC")):
    try:
        offset = _parse_tz(tz)
    except ValueError as e:
        return {"error": str(e)}
    now = datetime.now(timezone.utc) + offset
    return {
        "date": now.date().isoformat(),
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "weekday": now.strftime("%A"),
        "tz": tz,
    }


@app.get("/date/utc")
def get_date_utc(fmt: str = Query("iso")):
    now = datetime.now(timezone.utc)
    return _format(now, fmt, "UTC")


@app.get("/date/local")
def get_date_local(fmt: str = Query("iso")):
    now = datetime.now()
    return _format(now, fmt, "local")


def _parse_tz(tz: str) -> timedelta:
    if tz == "UTC":
        return timedelta(0)
    if tz.upper() == "LOCAL":
        return datetime.now().astimezone().utcoffset() or timedelta(0)
    # простой парсер для фиксированных смещений: +04:00, -03:30
    if len(tz) >= 3 and tz[0] in "+-" and tz[1:].count(":") == 1:
        sign = 1 if tz[0] == "+" else -1
        h, m = tz[1:].split(":")
        return timedelta(minutes=sign * (int(h) * 60 + int(m)))
    # известные IANA-подобные имена (ограниченный набор)
    fixed = {
        "Asia/Astrakhan": timedelta(hours=4),
        "Europe/Moscow": timedelta(hours=3),
        "Europe/London": timedelta(hours=0),
        "America/New_York": timedelta(hours=-5),
    }
    if tz in fixed:
        return fixed[tz]
    raise ValueError(f"unsupported timezone: {tz}")


def _format(dt: datetime, fmt: str, tz: str) -> dict:
    base = {"tz": tz}
    if fmt == "iso":
        return {**base, "iso": dt.isoformat(), "epoch": int(dt.timestamp())}
    if fmt == "epoch":
        return {**base, "epoch": int(dt.timestamp())}
    if fmt == "date":
        return {**base, "date": dt.date().isoformat()}
    if fmt == "time":
        return {**base, "time": dt.strftime("%H:%M:%S")}
    if fmt == "human":
        return {**base, "human": dt.strftime("%Y-%m-%d %H:%M:%S")}
    return {**base, "error": f"unknown format: {fmt}"}
