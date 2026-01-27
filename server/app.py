import math
import re
import urllib.parse
from datetime import datetime, timezone, timedelta
from typing import Tuple, Dict

import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from cachetools import TTLCache

from tithi import TITHIs, MASAs, RASHIs, Ayana, Ritu
from db import get_by_date, insert_row, start_tunnel, stop_tunnel, close_connection


app = FastAPI(title="Lunar Calendar API", version="1.0.0")

http = requests.Session()

cache = TTLCache(maxsize=512, ttl=12 * 60 * 60)

# in app.py add these lifecycle handlers (place near other top-level definitions)
@app.on_event("startup")
def startup():
    start_tunnel()

@app.on_event("shutdown")
def shutdown():
    close_connection()
    stop_tunnel()


# ------------------ utilities ------------------

def cartesian_to_longitude(x: float, y: float, z: float) -> float:
    lon = math.degrees(math.atan2(y, x))
    return lon % 360


def get_horizons_xyz(command: str, date: str) -> Tuple[float, float, float]:
    params = {
        "format": "json",
        "COMMAND": f"'{command}'",
        "CENTER": "'500@399'",
        "EPHEM_TYPE": "'VECTORS'",
        "START_TIME": f"'{date} 00:00'",
        "STOP_TIME": f"'{date} 00:01'",
        "STEP_SIZE": "'1 m'",
        "REF_PLANE": "'ECLIPTIC'",
        "REF_SYSTEM": "'J2000'",
        "OUT_UNITS": "'KM'",
    }

    query = urllib.parse.urlencode(params, safe="'@")
    url = "https://ssd.jpl.nasa.gov/api/horizons.api?" + query

    try:
        r = http.get(url, timeout=10)
        r.raise_for_status()
    except requests.RequestException:
        raise HTTPException(
            status_code=503,
            detail="Ephemeris service unavailable"
        )

    text = r.json().get("result", "")
    match = re.search(r"\$\$SOE(.*?)\$\$EOE", text, re.S)

    if not match:
        raise HTTPException(502, "Invalid ephemeris response")

    for line in match.group(1).splitlines():
        m = re.search(
            r"X\s*=\s*([-0-9.E+]+)\s*Y\s*=\s*([-0-9.E+]+)\s*Z\s*=\s*([-0-9.E+]+)",
            line
        )
        if m:
            return float(m.group(1)), float(m.group(2)), float(m.group(3))

    raise HTTPException(502, "Ephemeris parsing failed")


def get_ritu_from_longitude(lon: float) -> Ritu:
    lon %= 360
    if lon >= 330 or lon < 30:
        return Ritu.VASANTA
    if lon < 90:
        return Ritu.GRISHMA
    if lon < 150:
        return Ritu.VARSHA
    if lon < 210:
        return Ritu.SHARAD
    if lon < 270:
        return Ritu.HEMANTA
    return Ritu.SHISHIRA


# ------------------ response model ------------------

class LunarResponse(BaseModel):
    date: str

    ayana: str
    ritu: str
    masa: str
    paksha: str
    tithi: str
    phase: str

    surya_rashi: str
    chandra_rashi: str

    surya_longitude_deg: float
    chandra_longitude_deg: float
    longitudinal_angle_deg: float

    surya_xyz: Tuple[float, float, float]
    chandra_xyz: Tuple[float, float, float]


# ------------------ core service ------------------

def compute_ephemeris(date: str) -> Dict:
    print('computing...')
    moon_xyz = get_horizons_xyz("301", date)
    sun_xyz = get_horizons_xyz("10", date)

    sun_lon = cartesian_to_longitude(*sun_xyz)
    moon_lon = cartesian_to_longitude(*moon_xyz)

    angle = (moon_lon - sun_lon) % 360

    tithi = TITHIs[int(angle // 12)]
    masa = MASAs[int(sun_lon // 30)]
    surya_rashi = RASHIs[int(sun_lon // 30)]
    chandra_rashi = RASHIs[int(moon_lon // 30)]

    ayana = (
        Ayana.UTTARAYANA
        if sun_lon >= 270 or sun_lon < 90
        else Ayana.DAKSHINAYANA
    )

    return {
        "date": date,
        "ayana": ayana.value,
        "ritu": get_ritu_from_longitude(sun_lon).value,
        "masa": masa.value,
        "paksha": tithi.paksha.value,
        "tithi": tithi.name.value,
        "phase": "Waxing" if angle < 180 else "Waning",
        "surya_rashi": surya_rashi.value,
        "chandra_rashi": chandra_rashi.value,
        "surya_longitude_deg": sun_lon,
        "chandra_longitude_deg": moon_lon,
        "longitudinal_angle_deg": angle,
        "surya_xyz": sun_xyz,
        "chandra_xyz": moon_xyz,
    }


# ------------------ API ------------------

@app.get("/")
def index():
    return "hello world!"

@app.get(
    "/info",
    response_model=LunarResponse,
    status_code=200
)
def lunar_angle(
    date: str = Query(
        default=None,
        description="UTC date in YYYY-MM-DD"
    )
):
    if date is None:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format, expected YYYY-MM-DD"
        )

    if date in cache:
        return cache[date]

    row = get_by_date(date)
    if row:
        cache[date] = row
        return row

    data = compute_ephemeris(date)

    insert_row(data)
    cache[date] = data

    return data
