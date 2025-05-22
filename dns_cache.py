import sqlite3
from config import DB_PATH

def store_dns_cache(entries):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for entry in entries:
        c.execute("""
            INSERT INTO dns_cache (ip, hostname, zone, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(ip) DO UPDATE SET
                hostname=excluded.hostname,
                zone=excluded.zone,
                updated_at=CURRENT_TIMESTAMP
        """, (entry["ip"], entry["hostname"], entry.get("zone", "")))
    conn.commit()
    conn.close()

def load_dns_cache():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ip, hostname FROM dns_cache")
    rows = c.fetchall()
    conn.close()
    return {ip: hostname for ip, hostname in rows}

def get_dns_cache_age():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT MAX(updated_at) FROM dns_cache")
    row = c.fetchone()
    conn.close()
    return row[0] if row else None
