#!/usr/bin/env python3
import argparse
import sqlite3
import json
from tabulate import tabulate

DB_PATH = "netbox.db"

def list_snapshots():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT snapshot_date FROM ip_records ORDER BY snapshot_date DESC")
    for r in c.fetchall():
        print(r[0])
    conn.close()

def show_snapshot(date):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT ip, description, dns_name, tags
        FROM ip_records
        WHERE snapshot_date = ?
    """, (date,))
    rows = c.fetchall()
    print(tabulate(rows, headers=["IP", "Description", "DNS", "Tags"]))
    conn.close()

def show_diff(date):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT diff_json FROM ip_diffs WHERE compare_date = ?", (date,))
    result = c.fetchone()
    if result:
        diff = json.loads(result[0])
        print(json.dumps(diff, indent=2))
    else:
        print("Kein Diff für dieses Datum gefunden.")
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NetBox CLI Viewer")
    parser.add_argument("--list", action="store_true", help="Alle Snapshot-Daten anzeigen")
    parser.add_argument("--snapshot", type=str, help="Snapshot-Datum anzeigen")
    parser.add_argument("--diff", type=str, help="Diff für Datum anzeigen")
    args = parser.parse_args()

    if args.list:
        list_snapshots()
    elif args.snapshot:
        show_snapshot(args.snapshot)
    elif args.diff:
        show_diff(args.diff)
    else:
        parser.print_help()
