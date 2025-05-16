import sqlite3
import json
from datetime import datetime

DB_PATH = "netbox.db"

def is_valid_ip(ip):
    return isinstance(ip, str) and ip.count(".") == 3 and "/" in ip

def load_snapshot(conn, snapshot_date):
    c = conn.cursor()
    c.execute("SELECT ip, description, dns_name, tags FROM ip_records WHERE snapshot_date = ?", (snapshot_date,))
    return c.fetchall()

def clean_snapshots():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT DISTINCT snapshot_date FROM ip_records ORDER BY snapshot_date DESC")
    dates = [r[0] for r in c.fetchall()]
    removed = []

    for date in dates:
        rows = load_snapshot(conn, date)
        if not rows:
            continue

        first_ip = rows[0][0]
        if not is_valid_ip(first_ip):
            print(f"⚠️  Entferne fehlerhaften Snapshot: {date} ({first_ip})")
            c.execute("DELETE FROM ip_records WHERE snapshot_date = ?", (date,))
            c.execute("DELETE FROM ip_diffs   WHERE compare_date  = ?", (date,))
            conn.commit()
            removed.append(date)

    conn.close()

    if removed:
        print(f"\n🧹 Entfernt: {len(removed)} Snapshot(s):")
        for ts in removed:
            print(f" - {ts}")
    else:
        print("✅ Keine fehlerhaften Snapshots gefunden.")

if __name__ == "__main__":
    clean_snapshots()
