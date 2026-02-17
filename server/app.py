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

from pydantic import BaseModel, Field, field_validator
from cachetools import TTLCache

from type_info import TITHIs, MASAs, RASHIs, UPAVAASs, Ayana, Ritu
from db import get_by_date, insert_row, start_tunnel, stop_tunnel, close_connection


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

def cartesian_to_longitude(x: float, y: float, z: float) -> float:
    lon = math.degrees(math.atan2(y, x))
    return lon % 360


def get_horizons_xyz(command: str, date: str, center: str="399") -> Tuple[float, float, float]:
    params = {
        "format": "json",
        "COMMAND": f"'{command}'",
        "CENTER": f"'500@{center}'",
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


def resolve_upavaas( *, tithi, paksha, masa, sun_lon ) -> list[dict]:

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
                if not (270 <= sun_lon < 300):
                    continue

        results.append({
            "name": fd.name,
            "description": fd.description
        })

    return results


# ------------------ response model ------------------

class LunarInfoQuery(BaseModel):
    date: str | None = Field(
        default=None,
        description="UTC date in YYYY-MM-DD"
    )

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format, expected YYYY-MM-DD"
            )
            # raise ValueError("Invalid date format, expected YYYY-MM-DD")
        return v

class FastingInfo(BaseModel):
    name: str
    description: str

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

    upavaas: list[FastingInfo]


class PlanetCoordinate(BaseModel):
    name: str
    xyz: Tuple[float, float, float]
    longitude_deg: float

class PlanetsResponse(BaseModel):
    date: str
    planets: list[PlanetCoordinate]

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

    upavaas = resolve_upavaas(
        tithi=tithi,
        paksha=tithi.paksha,
        masa=masa,
        sun_lon=sun_lon
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
    date = query.date
    if date is None:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

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
    date = query.date
    if date is None:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Use a specific prefix for planet cache to avoid collisions with /info
    cache_key = f"planets_{date}"
    
    if cache_key in cache:
        return cache[cache_key]

    # No DB storage requested, just compute and cache
    data = compute_all_planets(date)
    cache[cache_key] = data

    return data