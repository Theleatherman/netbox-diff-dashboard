from flask import Flask, render_template, request
import sqlite3
import json
import ast
from datetime import datetime
from babel.dates import format_datetime as babel_format_datetime
import os
import logging
from dns_cache import load_dns_cache, get_dns_cache_age
from netbox import get_mgmt_ips
from config import DB_PATH, ACTIVE_THEME, ALLOWED_THEMES, FALLBACK_THEME


def resolve_active_theme() -> str:
    if ACTIVE_THEME in ALLOWED_THEMES:
        return ACTIVE_THEME
    logging.warning("Unbekanntes ACTIVE_THEME '%s' - fallback auf '%s'", ACTIVE_THEME, FALLBACK_THEME)
    return FALLBACK_THEME


RESOLVED_THEME = resolve_active_theme()
app = Flask(__name__, template_folder=f"templates/{RESOLVED_THEME}")

os.environ["LANG"] = "de_DE.UTF-8"
os.environ["LC_ALL"] = "de_DE.UTF-8"


@app.context_processor
def inject_theme_context():
    return {
        "active_theme": RESOLVED_THEME,
        "active_theme_requested": ACTIVE_THEME,
    }

# 📦 Alle Snapshot-Daten (für Dropdown)
def get_snapshot_dates():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    c = conn.cursor()
    c.execute("SELECT DISTINCT snapshot_date FROM ip_records ORDER BY snapshot_date DESC")
    dates = [r[0] for r in c.fetchall()]
    conn.close()
    return dates


def safe_parse_tags(tags):
    if not tags:
        return []
    try:
        return json.loads(tags)
    except (TypeError, json.JSONDecodeError):
        try:
            parsed = ast.literal_eval(tags)
            return parsed if isinstance(parsed, list) else []
        except (SyntaxError, ValueError):
            return []

# 🧠 Snapshot für ein bestimmtes Datum laden (inkl. Tag-Parsing)
def get_snapshot(date):
    conn = sqlite3.connect(DB_PATH, timeout=10)
    c = conn.cursor()
    c.execute("""
        SELECT ip, description, dns_name, tags
        FROM ip_records
        WHERE snapshot_date = ?
    """, (date,))
    rows = c.fetchall()
    conn.close()

    # Tags aus String in Liste umwandeln
    parsed = []
    for ip, desc, dns, tags in rows:
        tag_list = safe_parse_tags(tags)
        parsed.append((ip, desc, dns, tag_list))
    return parsed

# 📋 Diff-Daten als JSON-Objekt aus DB laden
def get_diff_by_date(date):
    conn = sqlite3.connect(DB_PATH, timeout=10)
    c = conn.cursor()
    c.execute("SELECT diff_json FROM ip_diffs WHERE compare_date = ?", (date,))
    result = c.fetchone()
    conn.close()
    return json.loads(result[0]) if result else {}

def format_datetime(iso_string):
    try:
        dt = datetime.fromisoformat(iso_string)
        return babel_format_datetime(dt, format="d. MMMM yyyy, HH:mm 'Uhr'", locale="de")
    except Exception:
        return iso_string  # Fallback bei Fehler

# 🌐 Hauptseite: Snapshot-Ansicht mit Tag-/Datum-Filter
@app.route("/")
def index():
    return render_template("home.html", year=datetime.now().year, active_page="home")  # neue Auswahlseite

# 🔍 Vergleichsansicht: Änderungen als Tabelle anzeigen
@app.route("/diffs")
def diffs():
    dates = get_snapshot_dates()
    selected_date = request.args.get("date") or (dates[0] if dates else None)
    readable_date = format_datetime(selected_date)
    diff_data = get_diff_by_date(selected_date)
    return render_template("diffs.html", diff=diff_data, dates=dates, selected_date=selected_date, readable_date=readable_date, year=datetime.now().year, active_page="diffs")

@app.route("/snapshots")
def snapshots():
    dates = get_snapshot_dates()
    selected_date = request.args.get("date") or (dates[0] if dates else None)
    snapshot = get_snapshot(selected_date) if selected_date else []
    readable_date = format_datetime(selected_date)
    return render_template("snapshots.html",
                           data=snapshot,
                           dates=dates,
                           selected_date=selected_date,
                           readable_date=readable_date,
                           year=datetime.now().year,
                           active_page="snapshots")

@app.route("/dns-diff")
def dns_diff_view():
    try:
        netbox_map = {
            ip.split("/")[0]: dns
            for (ip, desc, dns, tags) in get_mgmt_ips()
            if ip and dns and isinstance(dns, str)
        }
        dns_map = load_dns_cache()              # z. B. { "10.1.0.1": "host01" }

        only_in_netbox = {
            ip: netbox_map[ip]
            for ip in netbox_map
            if ip not in dns_map
        }

        only_in_dns = {
            ip: dns_map[ip]
            for ip in dns_map
            if ip not in netbox_map
        }

        mismatches = []
        for ip in netbox_map:
            if ip in dns_map:
                netbox_host = netbox_map[ip]
                dns_host = dns_map[ip]
                if (
                    isinstance(netbox_host, str)
                    and isinstance(dns_host, str)
                    and netbox_host.strip()
                    and dns_host.strip()
                    and netbox_host.strip().lower() != dns_host.strip().lower()
                ):
                    mismatches.append((ip, netbox_host, dns_host))

        diff = {
            "only_in_netbox": only_in_netbox,
            "only_in_dns": only_in_dns,
            "hostname_mismatches": mismatches
        }

        return render_template(
            "dns_diff.html",
            diff=diff,
            cache_age=get_dns_cache_age(),
            year=datetime.now().year,
            active_page="dns-diff"
        )

    except Exception as e:
        return render_template(
            "dns_diff.html",
            diff={
                "only_in_netbox": {},
                "only_in_dns": {},
                "hostname_mismatches": []
            },
            error=str(e),
            cache_age=None,
            year=datetime.now().year,
            active_page="dns-diff"
        )

# 🚀 Start
if __name__ == "__main__":
    import sys
    port = int(sys.argv[2]) if len(sys.argv) >= 3 and sys.argv[1] == "--port" else 8000
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="127.0.0.1", port=port, debug=debug)
