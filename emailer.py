import os
import smtplib
from html import escape
from dotenv import load_dotenv
from datetime import datetime
from babel.dates import format_datetime as babel_format_datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")

def send_email(subject, plain_body, html_body=None):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    part1 = MIMEText(plain_body, "plain", "utf-8")
    msg.attach(part1)

    if html_body:
        part2 = MIMEText(html_body, "html", "utf-8")
        msg.attach(part2)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            if SMTP_USER and SMTP_PASSWORD:
                server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
            print("📧 E-Mail erfolgreich gesendet.")
    except Exception as e:
        print(f"❌ Fehler beim Senden der E-Mail: {e}")

def format_datetime(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str)
        return babel_format_datetime(dt, format="d. MMMM yyyy, HH:mm 'Uhr'", locale="de")
    except Exception:
        return iso_str  # Fallback bei Fehler


def _fmt_value(value):
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value)


def render_diff_plain(diff, last_formatted=None, now_formatted=None):
    added = diff.get("added", [])
    removed = diff.get("removed", [])
    changed = diff.get("changed", {})
    change_rows = sum(len(fields) for fields in changed.values())

    lines = ["NetBox IP-Diff-Status", ""]

    if last_formatted and now_formatted:
        lines.append(f"Zeitraum: {last_formatted} bis {now_formatted}")
    lines.extend([
        f"Uebersicht: {len(added)} hinzugefuegt, {len(removed)} entfernt, {change_rows} Feldaenderungen auf {len(changed)} IPs.",
        "",
    ])

    if added:
        lines.append("== Hinzugefuegt ==")
        for ip, desc, dns, tags in added:
            lines.append(
                f"- {ip} | Beschreibung: {_fmt_value(desc)} | DNS: {_fmt_value(dns)} | Tags: {_fmt_value(tags)}"
            )
        lines.append("")

    if removed:
        lines.append("== Entfernt ==")
        for ip, desc, dns, tags in removed:
            lines.append(
                f"- {ip} | Beschreibung: {_fmt_value(desc)} | DNS: {_fmt_value(dns)} | Tags: {_fmt_value(tags)}"
            )
        lines.append("")

    if changed:
        lines.append("== Geaendert ==")
        for ip, changes in changed.items():
            lines.append(f"- {ip}")
            for field, change in changes.items():
                old_value = _fmt_value(change.get("old", ""))
                new_value = _fmt_value(change.get("new", ""))
                lines.append(f"  * {field}: '{old_value}' -> '{new_value}'")
        lines.append("")

    if not any([added, removed, changed]):
        lines.append("Keine Aenderungen.")
        lines.append("")

    lines.append("Weitere Informationen: https://netbox-diff.avemo-group.net/")
    return "\n".join(lines)
    
def render_diff_html(diff):
    year = datetime.now().year
    added = diff.get("added", [])
    removed = diff.get("removed", [])
    changed = diff.get("changed", {})
    change_rows = sum(len(fields) for fields in changed.values())

    html = """
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body { font-family: sans-serif; background: #0b0b0b; color: #e0e0e0; padding: 2em; }
        table { border-collapse: collapse; width: 100%; margin-top: 0.5em; }
        th, td { padding: 8px; border: 1px solid #444; text-align: left; }
        h3 { margin-top: 2em; }
        .summary { margin: 1em 0 1.5em 0; padding: 1em; border: 1px solid #333; background: #141414; }
        .summary strong { color: #fff; }
      </style>
      <link rel="stylesheet" href="/static/sentinex.css">
    </head>
    <body>
      <h1 style="color: #fff;">📦 NetBox IP-Diff-Status</h1>
    """

    html += f"""
      <div class="summary">
        <p><strong>Übersicht:</strong> {len(added)} hinzugefügt, {len(removed)} entfernt, {change_rows} Feldänderungen auf {len(changed)} IPs.</p>
      </div>
    """

    if added:
        html += "<h3 style='color:#4caf50;'>➕ Hinzugefügt</h3><table><thead><tr><th>IP</th><th>Beschreibung</th><th>DNS</th><th>Tags</th></tr></thead><tbody>"
        for ip, desc, dns, tags in added:
            html += (
                f"<tr><td>{escape(_fmt_value(ip))}</td>"
                f"<td>{escape(_fmt_value(desc))}</td>"
                f"<td>{escape(_fmt_value(dns))}</td>"
                f"<td>{escape(_fmt_value(tags))}</td></tr>"
            )
        html += "</tbody></table>"

    if removed:
        html += "<h3 style='color:#f44336;'>➖ Entfernt</h3><table><thead><tr><th>IP</th><th>Beschreibung</th><th>DNS</th><th>Tags</th></tr></thead><tbody>"
        for ip, desc, dns, tags in removed:
            html += (
                f"<tr><td>{escape(_fmt_value(ip))}</td>"
                f"<td>{escape(_fmt_value(desc))}</td>"
                f"<td>{escape(_fmt_value(dns))}</td>"
                f"<td>{escape(_fmt_value(tags))}</td></tr>"
            )
        html += "</tbody></table>"

    if changed:
        html += "<h3 style='color:#ff9800;'>🔁 Geändert</h3><table><thead><tr><th>IP</th><th>Feld</th><th>Alt</th><th>Neu</th></tr></thead><tbody>"
        for ip, changes in changed.items():
            for field, change in changes.items():
                html += (
                    f"<tr><td>{escape(_fmt_value(ip))}</td>"
                    f"<td>{escape(_fmt_value(field))}</td>"
                    f"<td>{escape(_fmt_value(change.get('old', '')))}</td>"
                    f"<td>{escape(_fmt_value(change.get('new', '')))}</td></tr>"
                )
        html += "</tbody></table>"

    if not any([added, removed, changed]):
        html += "<p style='color:#ccc;'>Keine Änderungen.</p>"

    html += f"""
      <p>Weitere Informationen unter: <a href="https://netbox-diff.avemo-group.net/">https://netbox-diff.avemo-group.net/</a></p>
    """

    html += f"""
      <hr style="margin-top: 2em; border: none; border-top: 1px solid #333;">
      <p style="font-size: 0.8em; color: #888;">
        Generated by <strong>netbox-ip-diff-dashboard</strong> ·
        Built with ❤️ by <a href="https://git.avemo-it.cloud/theleatherman/" style="color:#888;">The Leatherman</a> ·
        &copy; {year} <a href="https://www.sentinex.de/" style="color:#888;">sentinex GmbH</a>
      </p>
    </body>
    </html>
    """
    return html
