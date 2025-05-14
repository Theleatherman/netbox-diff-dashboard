import sqlite3
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript(open("schema.sql").read())
    conn.commit()
    conn.close()

def store_snapshot(ips, timestamp):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for ip in ips:
        c.execute("""
            INSERT INTO ip_records (snapshot_date, ip, description, dns_name, tags)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, ip["address"], ip["description"], ip["dns_name"], str(ip["tags"])))
    conn.commit()
    conn.close()

def load_latest_snapshot():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT ip, description, dns_name, tags FROM ip_records
        WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM ip_records)
    """)
    rows = c.fetchall()
    conn.close()
    return [
        {"address": r[0], "description": r[1], "dns_name": r[2], "tags": eval(r[3])}
        for r in rows
    ]

def store_diff(diff_json, timestamp):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO ip_diffs (compare_date, diff_json) VALUES (?, ?)", (timestamp, diff_json))
    conn.commit()
    conn.close()
