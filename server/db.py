import os
import json
from datetime import datetime as datetime_type
from datetime import datetime
import pymysql
from sshtunnel import SSHTunnelForwarder
from dotenv import load_dotenv

load_dotenv()

_tunnel = None
_connection = None


def start_tunnel():
    global _tunnel

    if _tunnel is not None and _tunnel.is_active:
        return

    _tunnel = SSHTunnelForwarder(
        (os.getenv("SSH_HOST"), 22),
        ssh_username=os.getenv("MYSQL_USER"),
        ssh_password=os.getenv("MYSQL_SSH_PASSWORD"),
        remote_bind_address=(
            os.getenv("MYSQL_HOST"),
            3306,
        ),
    )
    _tunnel.start()


def stop_tunnel():
    global _tunnel
    if _tunnel is not None and _tunnel.is_active:
        _tunnel.stop()
    _tunnel = None


def get_connection():
    global _connection

    if _connection is not None and _connection.open:
        return _connection

    start_tunnel()

    _connection = pymysql.connect(
        host="127.0.0.1",
        port=_tunnel.local_bind_port,
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),
        cursorclass=pymysql.cursors.DictCursor,
        charset="utf8mb4",
        autocommit=True,
        connect_timeout=10,
        read_timeout=30,
        write_timeout=30,
    )
    return _connection


def close_connection():
    global _connection
    if _connection is not None:
        _connection.close()
    _connection = None


def get_by_timestamp(timestamp: str):
    formatted_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")

    conn = get_connection()
    # AND grahana <> 'None'
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM lunar_ephemeris WHERE utc_stamp = %s AND upavaas IS NOT NULL",
            (formatted_time,),
        )
        row = cur.fetchone()
        if not row:
            return None

        row.pop("created_at", None)

        # normalize
        if isinstance(row["utc_stamp"], datetime_type):
            row["utc_stamp"] = row["utc_stamp"].isoformat()

        # normalize JSON -> tuple
        row["surya_xyz"] = tuple(json.loads(row["surya_xyz"]))
        row["chandra_xyz"] = tuple(json.loads(row["chandra_xyz"]))

        # normalize upavaas JSON -> list
        upavaas_raw = row.get("upavaas")
        if upavaas_raw is None or upavaas_raw == "null":
            return None
        elif isinstance(upavaas_raw, str):
            row["upavaas"] = json.loads(upavaas_raw)
        else:
            row["upavaas"] = upavaas_raw

        return row


def insert_row(data: dict):
    conn = get_connection()

    data = data.copy()
    raw_ts = data.get("timestamp") or data.get("date")
    
    # Standardize to string format if it isn't already a datetime object
    if isinstance(raw_ts, str):
        data["utc_stamp"] = raw_ts.replace("T", " ")
    else:
        data["utc_stamp"] = raw_ts

    data["grahana"] = data.get("grahana", "None")
    
    # Ensure JSON fields are strings without double-encoding
    data["surya_xyz"] = json.dumps(data["surya_xyz"]) if not isinstance(data["surya_xyz"], str) else data["surya_xyz"]
    data["chandra_xyz"] = json.dumps(data["chandra_xyz"]) if not isinstance(data["chandra_xyz"], str) else data["chandra_xyz"]
    data["upavaas"] = json.dumps(data.get("upavaas", [])) if not isinstance(data.get("upavaas"), str) else data.get("upavaas")

    with conn.cursor() as cur:
        # Notice how this is wrapped in () instead of """. 
        # This guarantees NO hidden indentation spaces are sent to MySQL.
        sql = (
            "INSERT INTO lunar_ephemeris ("
            "utc_stamp, ayana, ritu, masa, paksha, tithi, phase, "
            "surya_rashi, chandra_rashi, surya_longitude_deg, chandra_longitude_deg, "
            "longitudinal_angle_deg, grahana, surya_xyz, chandra_xyz, upavaas"
            ") VALUES ("
            "%(utc_stamp)s, %(ayana)s, %(ritu)s, %(masa)s, %(paksha)s, %(tithi)s, %(phase)s, "
            "%(surya_rashi)s, %(chandra_rashi)s, %(surya_longitude_deg)s, %(chandra_longitude_deg)s, "
            "%(longitudinal_angle_deg)s, %(grahana)s, %(surya_xyz)s, %(chandra_xyz)s, %(upavaas)s"
            ") ON DUPLICATE KEY UPDATE "
            "ayana=VALUES(ayana), ritu=VALUES(ritu), masa=VALUES(masa), "
            "paksha=VALUES(paksha), tithi=VALUES(tithi), phase=VALUES(phase), "
            "surya_rashi=VALUES(surya_rashi), chandra_rashi=VALUES(chandra_rashi), "
            "surya_longitude_deg=VALUES(surya_longitude_deg), chandra_longitude_deg=VALUES(chandra_longitude_deg), "
            "longitudinal_angle_deg=VALUES(longitudinal_angle_deg), grahana=VALUES(grahana), "
            "surya_xyz=VALUES(surya_xyz), chandra_xyz=VALUES(chandra_xyz), upavaas=VALUES(upavaas)"
        )
        cur.execute(sql, data)

    conn.commit()