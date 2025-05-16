from flask import Flask, render_template, request, redirect
import sqlite3
import json
import ast
from datetime import datetime
from babel.dates import format_datetime as babel_format_datetime
import locale
import os

app = Flask(__name__)
DB_PATH = "netbox.db"

os.environ["LANG"] = "de_DE.UTF-8"
os.environ["LC_ALL"] = "de_DE.UTF-8"

# 📦 Alle Snapshot-Daten (für Dropdown)
def get_snapshot_dates():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT snapshot_date FROM ip_records ORDER BY snapshot_date DESC")
    dates = [r[0] for r in c.fetchall()]
    conn.close()
    return dates

# 🧠 Snapshot für ein bestimmtes Datum laden (inkl. Tag-Parsing)
def get_snapshot(date):
    conn = sqlite3.connect(DB_PATH)
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
        try:
            tag_list = ast.literal_eval(tags) if isinstance(tags, str) else []
        except:
            tag_list = []
        parsed.append((ip, desc, dns, tag_list))
    return parsed

# 📋 Diff-Daten als JSON-Objekt aus DB laden
def get_diff_by_date(date):
    conn = sqlite3.connect(DB_PATH)
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

def index():
    # hole alle vorhandenen Snapshot-Daten
    dates = get_snapshot_dates()
    selected_date_raw = request.args.get("date") or (dates[0] if dates else None)
    selected_tag = request.args.get("tag")

    snapshot = get_snapshot(selected_date_raw) if selected_date_raw else []

    # Filter nach Tag im Python-Code
    if selected_tag:
        snapshot = [row for row in snapshot if selected_tag in row[3]]

    # lesbares Datumsformat erzeugen
    try:
        os.environ["LANG"] = "de_DE.UTF-8"
        os.environ["LC_ALL"] = "de_DE.UTF-8"
        locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
        dt = datetime.fromisoformat(selected_date_raw)
        human_date = dt.strftime("%d. %B %Y, %H:%M Uhr")
    except Exception as e:
        print("⚠️ Locale konnte nicht gesetzt werden:", e)
        human_date = selected_date_raw  # Fallback

    return render_template("index.html",
                           data=snapshot,
                           dates=dates,
                           selected_date=human_date,
                           selected_tag=selected_tag,
                           year=datetime.now().year)

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

# 🚀 Start
if __name__ == "__main__":
    import sys
    port = int(sys.argv[2]) if len(sys.argv) >= 3 and sys.argv[1] == "--port" else 8000
    app.run(host="0.0.0.0", port=port, debug=True)
