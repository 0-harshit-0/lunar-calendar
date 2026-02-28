import math
import re
import urllib.parse
from datetime import datetime, timezone, timedelta
from typing import Tuple, Dict

import requests
from fastapi import FastAPI, Request, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

from cachetools import TTLCache

from models import LunarInfoQuery, LunarResponse, PlanetsResponse
from type_info import TITHIs, MASAs, RASHIs, UPAVAASs, Ayana, Ritu
from db import get_by_timestamp, insert_row, start_tunnel, stop_tunnel, close_connection


app = FastAPI(title="Lunar Calendar API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

http = requests.Session()

cache = TTLCache(maxsize=512, ttl=12 * 60 * 60) #12hours

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["120/minute"]
)
# app.state.limiter = limiter # configure redis for multiple servers


# in app.py add these lifecycle handlers (place near other top-level definitions)
@app.on_event("startup")
def startup():
    start_tunnel()

@app.on_event("shutdown")
def shutdown():
    close_connection()
    stop_tunnel()

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"}
    )


# ------------------ utilities ------------------

def cartesian_to_latitude(x: float, y: float, z: float) -> float:
    r = math.sqrt(x*x + y*y + z*z)
    if r == 0:
        return 0.0
    value = max(-1.0, min(1.0, z / r))
    return math.degrees(math.asin(value))


def cartesian_to_longitude(x: float, y: float, z: float) -> float:
    lon = math.degrees(math.atan2(y, x))
    return lon % 360

def get_ritu_from_longitude(lon: float) -> Ritu:
    lon = lon % 360

    if 0 <= lon < 60:
        return Ritu.VASANTA
    if 60 <= lon < 120:
        return Ritu.GRISHMA
    if 120 <= lon < 180:
        return Ritu.VARSHA
    if 180 <= lon < 240:
        return Ritu.SHARAD
    if 240 <= lon < 300:
        return Ritu.HEMANTA
    return Ritu.SHISHIRA


def resolve_upavaas( *, tithi, paksha, masa, surya_lon ) -> list[dict]:
    results: list[dict] = []

    for fd in UPAVAASs:
        # --- tithi based ---
        if fd.tithi and fd.tithi != tithi.name:
            continue

        if fd.paksha and fd.paksha != tithi.paksha:
            continue

        if fd.masa and fd.masa != masa:
            continue

        # --- solar based ---
        if fd.upavaas_type.name == "SOLAR_BASED":
            if "Makara" in fd.name:
                if not (270 <= surya_lon < 300):
                    continue

        results.append({
            "name": fd.name,
            "description": fd.description
        })

    return results


# ------------------ core service ------------------

def get_horizons_xyz(command: str, timestamp: str, center: str="399") -> Tuple[float, float, float]:
    dt_start = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
    dt_stop = dt_start + timedelta(minutes=1)

    params = {
        "format": "json",
        "COMMAND": f"'{command}'",
        "CENTER": f"'500@{center}'",
        "EPHEM_TYPE": "'VECTORS'",
        "START_TIME": f"'{dt_start.strftime("%Y-%m-%d %H:%M:%S")}'",
        "STOP_TIME": f"'{dt_stop.strftime("%Y-%m-%d %H:%M:%S")}'",
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


def compute_ephemeris(timestamp: str) -> Dict:
    print('computing...')

    surya_xyz = get_horizons_xyz("10", timestamp)
    chandra_xyz = get_horizons_xyz("301", timestamp)

    surya_lon = cartesian_to_longitude(*surya_xyz)
    chandra_lon = cartesian_to_longitude(*chandra_xyz)
    chandra_lat = cartesian_to_latitude(*chandra_xyz)

    angle = (chandra_lon - surya_lon) % 360

    ayana = (
        Ayana.UTTARAYANA
        if surya_lon >= 270 or surya_lon < 90
        else Ayana.DAKSHINAYANA
    )

    angle_norm = angle % 360
    surya_lon_norm = surya_lon % 360
    chandra_lon_norm = chandra_lon % 360

    tithi_index = min(int(angle_norm // 12), 29)
    masa_index = min(int(surya_lon_norm // 30), 11)
    surya_rashi_index = min(int(surya_lon_norm // 30), 11)
    chandra_rashi_index = min(int(chandra_lon_norm // 30), 11)

    tithi = TITHIs[tithi_index]
    masa = MASAs[masa_index]
    surya_rashi = RASHIs[surya_rashi_index]
    chandra_rashi = RASHIs[chandra_rashi_index]

    # ---- eclipse detection ----
    grahana = "None"

    # Strict astronomical thresholds
    CONJUNCTION_THRESHOLD = 1.0     # degrees
    OPPOSITION_THRESHOLD = 1.0      # degrees
    NODE_LAT_THRESHOLD = 0.5        # degrees

    is_conjunction = angle_norm < CONJUNCTION_THRESHOLD or angle_norm > 360 - CONJUNCTION_THRESHOLD
    is_opposition = abs(angle_norm - 180) < OPPOSITION_THRESHOLD
    near_node = abs(chandra_lat) < NODE_LAT_THRESHOLD

    if is_conjunction and near_node:
        grahana = "Surya"

    elif is_opposition and near_node:
        grahana = "Chandra"

    upavaas = resolve_upavaas(
        tithi=tithi,
        paksha=tithi.paksha,
        masa=masa,
        surya_lon=surya_lon
    )

    return {
        "timestamp": timestamp,
        "ayana": ayana.value,
        "ritu": get_ritu_from_longitude(surya_lon).value,
        "masa": masa.value,
        "paksha": tithi.paksha.value,
        "tithi": tithi.name.value,
        "phase": "Waxing" if angle_norm < 180 else "Waning",
        "surya_rashi": surya_rashi.value,
        "chandra_rashi": chandra_rashi.value,
        "surya_longitude_deg": surya_lon,
        "chandra_longitude_deg": chandra_lon,
        "longitudinal_angle_deg": angle,
        "grahana": grahana,
        "surya_xyz": surya_xyz,
        "chandra_xyz": chandra_xyz,
        "upavaas": upavaas,
    }


def compute_all_planets(date: str) -> Dict:
    planet_data = []
    
    for name, cmd in PLANET_MAP.items():
        xyz = get_horizons_xyz(cmd, date, "10")
        lon = cartesian_to_longitude(*xyz)
        planet_data.append({
            "name": name,
            "xyz": xyz,
            "longitude_deg": round(lon, 4)
        })
    
    return {
        "date": date,
        "planets": planet_data
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
@limiter.limit("60/minute")
def lunar_angle(
    request: Request,
    query: LunarInfoQuery = Depends()
):
    timestamp = query.timestamp
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    if timestamp in cache:
        return cache[timestamp]

    # return from cache if present
    row = get_by_timestamp(timestamp)
    if row:
        cache[timestamp] = row
        return row

    # compute
    data = compute_ephemeris(timestamp)

    # store and cache
    insert_row(data)
    cache[timestamp] = data

    return data


# Mapping of names to NASA Horizons IDs
# 10=Sun, 199=Mercury, 299=Venus, 301=Moon, 499=Mars, 599=Jupiter, 699=Saturn, 799=Uranus, 899=Neptune, 399=Earth
PLANET_MAP = {
    "Sun": "10",
    "Earth": "399",
    "Mercury": "199",
    "Venus": "299",
    "Mars": "499",
    "Jupiter": "599",
    "Saturn": "699",
    "Uranus": "799",
    "Neptune": "899"
}

@app.get(
    "/planets",
    # response_model=PlanetsResponse, # Uncomment if you want strict validation
    status_code=200
)
@limiter.limit("60/minute")
def get_planets(
    request: Request,
    query: LunarInfoQuery = Depends()
):
    input_date = query.timestamp
    
    # If no date provided, get today at midnight
    if input_date is None:
        target_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00")
    else:
        # Force whatever string the user sent to midnight
        # We take the first 10 chars (YYYY-MM-DD) and append 00:00:00
        # This handles '2026-02-28' or '2026-02-28T14:30:00'
        target_timestamp = f"{input_date[:10]}T00:00:00"

    # Cache key uses the normalized midnight timestamp
    cache_key = f"planets_{target_timestamp}"
    
    if cache_key in cache:
        return cache[cache_key]

    # compute_all_planets now receives 'YYYY-MM-DDT00:00:00'
    data = compute_all_planets(target_timestamp)
    cache[cache_key] = data

    return data