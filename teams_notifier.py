"""Microsoft Teams Incoming-Webhook notification for NetBox IP diffs.

Uses the Adaptive-Card format supported by the Teams Workflows connector
(as well as the legacy Office 365 Connector / MessageCard format as fallback).
A single webhook URL is all that is required; set TEAMS_WEBHOOK_URL in .env.
"""

import os

import requests
from dotenv import load_dotenv

from config import TEAMS_WEBHOOK_URL

load_dotenv()

_DASHBOARD_URL = os.getenv("DASHBOARD_URL", "https://netbox-diff.avemo-group.net/")


def _fmt(value):
    if isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value) or "–"
    return str(value) if value else "–"


def _rows_table(entries, label, color):
    """Return an Adaptive Card ColumnSet block for added/removed entries."""
    facts = []
    for ip, desc, dns, tags in entries:
        facts.append(
            {
                "type": "FactSet",
                "facts": [
                    {"title": "IP", "value": _fmt(ip)},
                    {"title": "Beschreibung", "value": _fmt(desc)},
                    {"title": "DNS", "value": _fmt(dns)},
                    {"title": "Tags", "value": _fmt(tags)},
                ],
                "separator": True,
            }
        )
    return [
        {
            "type": "TextBlock",
            "text": label,
            "weight": "Bolder",
            "color": color,
            "size": "Medium",
            "spacing": "Large",
        },
        *facts,
    ]


def _changed_table(changed):
    """Return Adaptive Card blocks for the changed-IP section."""
    blocks = [
        {
            "type": "TextBlock",
            "text": "🔁 Geändert",
            "weight": "Bolder",
            "color": "Warning",
            "size": "Medium",
            "spacing": "Large",
        }
    ]
    for ip, changes in changed.items():
        lines = [f"**{_fmt(ip)}**"]
        for field, change in changes.items():
            old_val = _fmt(change.get("old", ""))
            new_val = _fmt(change.get("new", ""))
            lines.append(f"- {field}: ~~{old_val}~~ → {new_val}")
        blocks.append(
            {
                "type": "TextBlock",
                "text": "\n\n".join(lines),
                "wrap": True,
                "separator": True,
            }
        )
    return blocks


def build_adaptive_card(subject, diff, last_formatted=None, now_formatted=None):
    """Build an Adaptive Card payload for Teams."""
    added = diff.get("added", [])
    removed = diff.get("removed", [])
    changed = diff.get("changed", {})
    change_rows = sum(len(fields) for fields in changed.values())

    summary_text = (
        f"{len(added)} hinzugefügt · {len(removed)} entfernt · "
        f"{change_rows} Feldänderungen auf {len(changed)} IPs"
    )
    if last_formatted and now_formatted:
        period_text = f"Zeitraum: **{last_formatted}** bis **{now_formatted}**"
    else:
        period_text = ""

    body = [
        {
            "type": "TextBlock",
            "text": subject,
            "weight": "Bolder",
            "size": "Large",
            "wrap": True,
        },
    ]
    if period_text:
        body.append({"type": "TextBlock", "text": period_text, "wrap": True})

    body.append(
        {
            "type": "TextBlock",
            "text": summary_text,
            "wrap": True,
            "spacing": "Medium",
        }
    )

    if added:
        body.extend(_rows_table(added, "➕ Hinzugefügt", "Good"))
    if removed:
        body.extend(_rows_table(removed, "➖ Entfernt", "Attention"))
    if changed:
        body.extend(_changed_table(changed))

    if not any([added, removed, changed]):
        body.append(
            {
                "type": "TextBlock",
                "text": "Keine Änderungen.",
                "color": "Default",
                "spacing": "Medium",
            }
        )

    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": body,
                    "actions": [
                        {
                            "type": "Action.OpenUrl",
                            "title": "Im Dashboard öffnen",
                            "url": _DASHBOARD_URL,
                        }
                    ],
                },
            }
        ],
    }
    return payload


def send_teams_notification(subject, diff, last_formatted=None, now_formatted=None):
    """Send a Teams notification for a diff.  Silently skipped when no webhook URL is set."""
    webhook_url = TEAMS_WEBHOOK_URL
    if not webhook_url:
        print(
            "ℹ️  TEAMS_WEBHOOK_URL nicht gesetzt – Teams-Benachrichtigung übersprungen."
        )
        return

    payload = build_adaptive_card(subject, diff, last_formatted, now_formatted)
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=15,
        )
        response.raise_for_status()
        print("💬 Teams-Benachrichtigung erfolgreich gesendet.")
    except requests.RequestException as exc:
        print(f"❌ Fehler beim Senden der Teams-Benachrichtigung: {exc}")
