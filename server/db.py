import os
import json
from datetime import date as date_type
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


def get_by_date(date: str):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM lunar_ephemeris WHERE date = %s AND fasting_days IS NOT NULL",
            (date,),
        )
        row = cur.fetchone()
        if not row:
            return None

        row.pop("created_at", None)

        # normalize date -> str
        if isinstance(row["date"], date_type):
            row["date"] = row["date"].isoformat()

        # normalize JSON -> tuple
        row["surya_xyz"] = tuple(json.loads(row["surya_xyz"]))
        row["chandra_xyz"] = tuple(json.loads(row["chandra_xyz"]))

        # normalize fasting_days JSON -> list
        raw = row.get("fasting_days")
        print("raw", raw)
        if raw is None or raw == "null":
            return None
            # row["fasting_days"] = []
        elif isinstance(raw, str):
            row["fasting_days"] = json.loads(raw)
        else:
            row["fasting_days"] = raw

        return row


def insert_row(data: dict):
    conn = get_connection()

    data = data.copy()
    data["surya_xyz"] = json.dumps(data["surya_xyz"])
    data["chandra_xyz"] = json.dumps(data["chandra_xyz"])
    data["fasting_days"] = json.dumps(data.get("fasting_days", []))

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO lunar_ephemeris (
                date, ayana, ritu, masa, paksha, tithi, phase,
                surya_rashi, chandra_rashi,
                surya_longitude_deg, chandra_longitude_deg,
                longitudinal_angle_deg,
                surya_xyz, chandra_xyz, fasting_days
            )
            VALUES (
                %(date)s, %(ayana)s, %(ritu)s, %(masa)s,
                %(paksha)s, %(tithi)s, %(phase)s,
                %(surya_rashi)s, %(chandra_rashi)s,
                %(surya_longitude_deg)s, %(chandra_longitude_deg)s,
                %(longitudinal_angle_deg)s,
                %(surya_xyz)s, %(chandra_xyz)s, %(fasting_days)s
            )
            ON DUPLICATE KEY UPDATE
                ayana = VALUES(ayana),
                ritu = VALUES(ritu),
                masa = VALUES(masa),
                paksha = VALUES(paksha),
                tithi = VALUES(tithi),
                phase = VALUES(phase),
                surya_rashi = VALUES(surya_rashi),
                chandra_rashi = VALUES(chandra_rashi),
                surya_longitude_deg = VALUES(surya_longitude_deg),
                chandra_longitude_deg = VALUES(chandra_longitude_deg),
                longitudinal_angle_deg = VALUES(longitudinal_angle_deg),
                surya_xyz = VALUES(surya_xyz),
                chandra_xyz = VALUES(chandra_xyz),
                fasting_days = VALUES(fasting_days)
            """,
            data,
        )
