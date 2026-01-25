
from flask import Flask, request, jsonify
import requests
import re
import urllib.parse
import math

from tithi import TITHIs, MASAs, RASHIs, Ayana, Ritu


app = Flask(__name__)

def cartesian_to_longitude(x, y, z):
    lon = math.atan2(y, x)
    lon_deg = math.degrees(lon)
    if lon_deg < 0:
        lon_deg += 360
    return lon_deg


def get_horizons_xyz(command, date, center="500@399", units="KM"):
    start_time = f"{date} 00:00"
    stop_time  = f"{date} 00:01"

    params = {
        "format": "json",
        "COMMAND": f"'{command}'",
        "CENTER": f"'{center}'",
        "EPHEM_TYPE": "'VECTORS'",
        "START_TIME": f"'{start_time}'",
        "STOP_TIME": f"'{stop_time}'",
        "STEP_SIZE": "'1 m'",
        "REF_PLANE": "'ECLIPTIC'",
        "REF_SYSTEM": "'J2000'",
        "OUT_UNITS": f"'{units}'"
    }

    query = urllib.parse.urlencode(params, safe="'@")
    url = "https://ssd.jpl.nasa.gov/api/horizons.api?" + query

    r = requests.get(url, timeout=60)
    r.raise_for_status()
    text = r.json().get("result", "")

    match = re.search(r"\$\$SOE(.*?)\$\$EOE", text, re.S)
    if not match:
        raise ValueError("Ephemeris block not found")

    for line in match.group(1).splitlines():
        m = re.search(
            r"X\s*=\s*([-0-9.E+]+)\s*Y\s*=\s*([-0-9.E+]+)\s*Z\s*=\s*([-0-9.E+]+)",
            line
        )
        if m:
            return float(m.group(1)), float(m.group(2)), float(m.group(3))

    raise ValueError("XYZ not found")


def get_ritu_from_longitude(sun_lon: float) -> Ritu:
    sun_lon = sun_lon % 360

    if sun_lon >= 330 or sun_lon < 30:
        return Ritu.VASANTA
    elif sun_lon < 90:
        return Ritu.GRISHMA
    elif sun_lon < 150:
        return Ritu.VARSHA
    elif sun_lon < 210:
        return Ritu.SHARAD
    elif sun_lon < 270:
        return Ritu.HEMANTA
    else:
        return Ritu.SHISHIRA


@app.route("/lunar-angle")
def lunar_angle():
    date = request.args.get("date", "2026-01-20")

    moon_xyz = get_horizons_xyz("301", date)
    sun_xyz  = get_horizons_xyz("10", date)

    sun_lon  = cartesian_to_longitude(*sun_xyz)
    moon_lon = cartesian_to_longitude(*moon_xyz)

    angle = moon_lon - sun_lon % 360

    phase = "Waxing" if angle > 0 else "Waning"
    tithi = TITHIs[int(angle//12)]
    masa = MASAs[int(sun_lon//30)]
    srashi = RASHIs[int(sun_lon//30)]
    crashi = RASHIs[int(moon_lon//30)]

    ayana_sun_lon = sun_lon % 360
    if ayana_sun_lon >= 270 or ayana_sun_lon < 90:
        ayana = Ayana.UTTARAYANA
    else:
        ayana = Ayana.DAKSHINAYANA

    ritu = get_ritu_from_longitude(sun_lon).value

    # return (
    #     f"Date: {date}\n"
    #     f"Sun longitude: {sun_lon:.6f}°\n"
    #     f"Moon longitude: {moon_lon:.6f}°\n"
    #     f"Longitudinal angle (Moon − Sun): {angle:.6f}°\n"
    #     f"Phase: {phase}\n"
    # )
    return jsonify({
          "date": date,
          "sun": {
              "longitude_deg": sun_lon,
              "xyz": sun_xyz
          },
          "moon": {
              "longitude_deg": moon_lon,
              "xyz": moon_xyz
          },
          "longitudinal_angle_deg": angle,
          "ayana": ayana.value,
          "masa": masa.value,
          "paksha": tithi.paksha.value,
          "tithi": tithi.name.value,
          "surya_rashi": srashi.value,
          "chandra_rashi": crashi.value,
          "ritu": ritu,
          "phase": phase
      })

