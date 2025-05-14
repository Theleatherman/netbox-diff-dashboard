from datetime import datetime
from db import init_db, store_snapshot, load_latest_snapshot, store_diff
from netbox import get_mgmt_ips
from diffing import compare_snapshots, diff_to_json
from emailer import send_mail
from jinja2 import Template
import locale

# Stelle sicher, dass dein System deutsche Lokalisierung unterstützt:
locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")

# Beispiel: Formatieren eines Snapshot-Timestamps
snapshot_date = datetime.now()  # oder datetime.now()
selected_date = snapshot_date.strftime("%d. %B %Y, %H:%M Uhr")

def main():
    init_db()
    now = datetime.now().isoformat()

    current = get_mgmt_ips()
    previous = load_latest_snapshot()
    diff = compare_snapshots(current, previous)

    store_snapshot(current, now)
    diff_json = diff_to_json(diff)
    store_diff(diff_json, now)

    with open("template.html") as f:
        html = Template(f.read()).render(diff=diff)

    with open("report.html", "w") as f:
        f.write(html)

    subject = "NetBox IP Änderungen" if diff else "NetBox: keine Änderungen"
    send_mail(html, subject)

if __name__ == "__main__":
    main()
