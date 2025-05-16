from emailer import send_email, render_diff_html
from datetime import datetime

dummy_diff = {
    "added": [
        ["10.1.1.1/24", "Neue Firewall", "fw01", ["firewall", "mgmt-if"]]
    ],
    "removed": [
        ["10.1.1.2/24", "Altes Backend", "backend01", ["dmz", "db"]]
    ],
    "changed": {
        "10.1.1.3/24": {
            "description": {"old": "Webserver alt", "new": "Webserver neu"},
            "tags": {"old": ["dmz"], "new": ["dmz", "vpn"]}
        }
    }
}

now = datetime.now().strftime("%d.%m.%Y %H:%M")
subject = f"📧 Test: Snapshot-Diff-Vorschau ({now})"
body_html = render_diff_html(dummy_diff)
body_plain = "Dies ist eine Testmail mit Beispiel-Änderungen (bitte HTML-Ansicht aktivieren)."

send_email(subject, body_plain, body_html)
