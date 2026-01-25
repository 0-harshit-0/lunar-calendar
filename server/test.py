# this script is just for understanding and testing

import requests
import re
import urllib.parse
import json
import math

from tithi import TITHIS

def cartesian_to_longitude(x, y, z):
    """
    Convert Cartesian coordinates to ecliptic longitude (in degrees).
    """
    # Compute longitude from X and Y
    lon = math.atan2(y, x)  # result in radians
    lon_deg = math.degrees(lon)  # convert to degrees

    # Normalize to 0 … 360 degrees
    if lon_deg < 0:
        lon_deg += 360

    return lon_deg


def get_horizons_xyz(command="301", center="500@399", date="2026-01-20", units="KM"):
    # Create a small time range for Horizons VECTORS
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

    json_res = r.json()  # full raw response
    text = json_res.get("result", "")

    # find the VECTORS block
    match_block = re.search(r"\$\$SOE(.*?)\$\$EOE", text, re.S)
    if not match_block:
        raise ValueError("Could not find state vector block in Horizons response")

    lines = match_block.group(1).splitlines()

    # parse XYZ
    xyz = None
    for line in lines:
        m = re.search(
            r"X\s*=\s*([-0-9.E+]+)\s*Y\s*=\s*([-0-9.E+]+)\s*Z\s*=\s*([-0-9.E+]+)",
            line,
        )
        if m:
            xyz = {
                "x": float(m.group(1)),
                "y": float(m.group(2)),
                "z": float(m.group(3)),
                "units": units
            }
            break

    if xyz is None:
        raise ValueError("Could not extract XYZ from Horizons output")

    return json_res, xyz


if __name__ == "__main__":
    date = "2026-01-20"

    # get raw and parsed for Moon
    moon_raw, moon_xyz = get_horizons_xyz("301", date=date)

    # get raw and parsed for Sun
    sun_raw, sun_xyz   = get_horizons_xyz("10",  date=date)

    # full JSON for file
    full_data = {
        "date": date,
        "moon": {
            "raw_response": moon_raw,
            "xyz": moon_xyz
        },
        "sun": {
            "raw_response": sun_raw,
            "xyz": sun_xyz
        }
    }

    # Save to pretty JSON file
    filename = "horizons_vectors.json"
    with open(filename, "w") as f:
        json.dump(full_data, f, indent=4)
        
    print(f"Saved vector data to: {filename}")

    moon_lon = cartesian_to_longitude(moon_xyz["x"], moon_xyz["y"], moon_xyz["z"])
    sun_lon  = cartesian_to_longitude(sun_xyz["x"],  sun_xyz["y"],  sun_xyz["z"])

    # difference
    longitudinal_angle = moon_lon - sun_lon
    delta = longitudinal_angle % 360

    masa_index = int(sun_lon // 30)   # 0 to 11

    print("Sun longitude:", sun_lon)
    print("Moon longitude:", moon_lon)
    print("Longitudinal angle (Moon - Sun):", longitudinal_angle, delta, int(delta//12))
    print("Tithi:", TITHIS[int(delta // 12)], masa_index)



