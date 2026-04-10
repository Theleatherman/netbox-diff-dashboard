import sqlite3
import json
import ast
from config import DB_PATH


def parse_tags(raw):
    if raw is None:
        return []
    if isinstance(raw, list):
        return raw
    try:
        return json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        try:
            parsed = ast.literal_eval(raw)
            return parsed if isinstance(parsed, list) else []
        except (SyntaxError, ValueError):
            return []


def init_db():
    with sqlite3.connect(DB_PATH, timeout=10) as conn:
        c = conn.cursor()
        c.executescript(open("schema.sql").read())
        conn.commit()


def store_snapshot(ips, timestamp):
    with sqlite3.connect(DB_PATH, timeout=10) as conn:
        c = conn.cursor()
        for ip in ips:
            c.execute(
                """
                INSERT INTO ip_records (snapshot_date, ip, description, dns_name, tags)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    ip["address"],
                    ip["description"],
                    ip["dns_name"],
                    json.dumps(ip["tags"]),
                ),
            )
        conn.commit()


def load_latest_snapshot():
    with sqlite3.connect(DB_PATH, timeout=10) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT ip, description, dns_name, tags FROM ip_records
            WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM ip_records)
        """)
        rows = c.fetchall()
    return [
        {
            "address": r[0],
            "description": r[1],
            "dns_name": r[2],
            "tags": parse_tags(r[3]),
        }
        for r in rows
    ]


def store_diff(diff_json, timestamp):
    with sqlite3.connect(DB_PATH, timeout=10) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO ip_diffs (compare_date, diff_json) VALUES (?, ?)",
            (timestamp, diff_json),
        )
        conn.commit()
