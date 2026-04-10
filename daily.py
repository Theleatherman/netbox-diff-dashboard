#!/usr/bin/env python3
import sqlite3
import json
import ipaddress
from datetime import datetime
from netbox import get_ips
from emailer import send_email, format_datetime, render_diff_html, render_diff_plain
import ast
from config import DB_PATH


def normalize(data):
    normalized = []
    for ip, desc, dns, tags in data:
        normalized.append(
            (ip.strip(), (desc or "").strip(), (dns or "").strip(), tuple(sorted(tags)))
        )
    return sorted(normalized)


def get_last_snapshot(conn):
    c = conn.cursor()
    c.execute(
        "SELECT DISTINCT snapshot_date FROM ip_records ORDER BY snapshot_date DESC LIMIT 1"
    )
    row = c.fetchone()
    return row[0] if row else None


def safe_parse_tags(raw):
    if not raw:
        return []
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        try:
            return ast.literal_eval(raw)
        except Exception:
            return []


def get_snapshot_data(conn, date):
    c = conn.cursor()
    c.execute(
        "SELECT ip, description, dns_name, tags FROM ip_records WHERE snapshot_date = ?",
        (date,),
    )
    rows = c.fetchall()
    parsed = []
    for ip, desc, dns, tags in rows:
        tag_list = safe_parse_tags(tags)
        parsed.append((ip, desc, dns, tag_list))
    return parsed


def store_snapshot(conn, snapshot_date, data):
    c = conn.cursor()
    for ip, desc, dns, tags in data:
        c.execute(
            """
            INSERT INTO ip_records (snapshot_date, ip, description, dns_name, tags)
            VALUES (?, ?, ?, ?, ?)
        """,
            (snapshot_date, ip, desc, dns, json.dumps(tags)),
        )
    conn.commit()


def build_diff(previous, current):
    # Index nach IP
    prev_map = {ip: (desc, dns, tags) for ip, desc, dns, tags in previous}
    curr_map = {ip: (desc, dns, tags) for ip, desc, dns, tags in current}

    added_ips = set(curr_map.keys()) - set(prev_map.keys())
    removed_ips = set(prev_map.keys()) - set(curr_map.keys())
    common_ips = set(curr_map.keys()) & set(prev_map.keys())

    diff = {
        "added": [[ip, *curr_map[ip]] for ip in added_ips],
        "removed": [[ip, *prev_map[ip]] for ip in removed_ips],
        "changed": {},
    }

    for ip in common_ips:
        prev_desc, prev_dns, prev_tags = prev_map[ip]
        curr_desc, curr_dns, curr_tags = curr_map[ip]

        changes = {}
        if prev_desc != curr_desc:
            changes["description"] = {"old": prev_desc, "new": curr_desc}
        if prev_dns != curr_dns:
            changes["dns_name"] = {"old": prev_dns, "new": curr_dns}
        if sorted(prev_tags) != sorted(curr_tags):
            changes["tags"] = {"old": sorted(prev_tags), "new": sorted(curr_tags)}

        if changes:
            diff["changed"][ip] = changes

    return diff


def store_diff(conn, date, diff):
    c = conn.cursor()
    c.execute(
        "INSERT INTO ip_diffs (compare_date, diff_json) VALUES (?, ?)",
        (date, json.dumps(diff, indent=2)),
    )
    conn.commit()


def is_valid_ip(ip):
    if not isinstance(ip, str):
        return False
    ip = ip.strip()
    if "/" not in ip:
        return False
    try:
        # NetBox stores addresses with prefix length (IPv4 and IPv6).
        ipaddress.ip_interface(ip)
        return True
    except ValueError:
        return False


def validate_snapshot(data):
    if not isinstance(data, list):
        print("❌ Snapshot ist kein Listentyp.")
        return False
    if len(data) == 0:
        print("❌ Snapshot ist leer.")
        return False

    for i, entry in enumerate(data):
        if not isinstance(entry, (list, tuple)):
            print(f"❌ Zeile {i} ist kein Tupel/Eintrag: {entry}")
            return False
        if len(entry) < 1:
            print(f"❌ Zeile {i} ist leer.")
            return False
        if not is_valid_ip(entry[0]):
            print(f"❌ Ungültige IP in Zeile {i}: {entry[0]}")
            return False
    return True


def main():
    now = datetime.now().isoformat()
    print(f"📦 Erzeuge Snapshot: {now}")

    current = get_ips()
    if not validate_snapshot(current):
        print(f"❌ Snapshot am {now} ungültig – keine Daten gespeichert.")
        return

    conn = sqlite3.connect(DB_PATH, timeout=10)
    last_date = get_last_snapshot(conn)
    previous = get_snapshot_data(conn, last_date) if last_date else []

    current_norm = normalize(current)
    previous_norm = normalize(previous)

    last_formatted = format_datetime(last_date) if last_date else "–"
    now_formatted = format_datetime(now)

    if current_norm != previous_norm:
        print("📝 Änderungen erkannt – Snapshot wird gespeichert.")
        diff = build_diff(previous_norm, current_norm)
        store_snapshot(conn, now, current)
        store_diff(conn, now, diff)

        subject = f"NetBox Snapshot-Diff (alle Änderungen) am {now_formatted}"
        body_plain = render_diff_plain(diff, last_formatted, now_formatted)
        body_html = render_diff_html(diff)

        send_email(subject, body_plain, body_html)
        print("✅ Snapshot gespeichert und E-Mail versendet.")

    else:
        print("📭 Keine Änderungen – Snapshot nicht gespeichert.")
        subject = f"NetBox Snapshot am {now_formatted}"
        body_plain = f"Keine Änderungen seit dem letzten Snapshot ({last_formatted})."
        body_html = f"""
        <html>
        <body style="font-family: sans-serif; background-color: #0b0b0b; color: #ccc; padding: 2em;">
          <h2>📦 NetBox IP-Diff-Status – Keine Änderungen</h2>
          <p>Seit dem letzten Snapshot vom <strong>{last_formatted}</strong> wurden keine Änderungen festgestellt.</p>
          <p style="margin-top:2em; font-size: 0.9em;">Snapshot erstellt am <strong>{now_formatted}</strong>.</p>
        </body>
        </html>
        """
        send_email(subject, body_plain, body_html)


if __name__ == "__main__":
    main()
