# 🛰️ NetBox IP Diff Dashboard

Ein schlankes, CI-konformes Dashboard zur täglichen Auswertung von IP-Daten aus der NetBox-API.  
Visualisiert IP-Zustände, ermöglicht Tag-Filter, Volltextsuche, Differenzvergleiche zwischen Snapshots und bietet ein modernes Webfrontend im Sentinex-Stil.

---

## 📦 Features

- 🔁 **Täglicher Snapshot** aller IP-Adressen aus NetBox mit Beschreibung/DNS/Tags
- 🕵️ **Filterung nach Tags**
- 🔍 **Volltextsuche** über IP, Beschreibung & DNS
- 📊 **DataTables-Integration** für Sortierung, Pagination & Suche
- 🏷️ Tags in Badge-Optik, an NetBox UI angelehnt
- 🧠 Automatische **Diff-Berechnung zwischen Snapshots**
- 🌙 **Dark Mode UI** im Sentinex-Design (anpassbar per CSS)
- 🧾 **Responsive** für Tablets / kleine Displays
- 💬 Lokalisierung in Deutsch
- 📥 SQLite-basiertes Datenlog
- ❤️ Footer: „Made with ❤️ by The Leatherman | sentinex GmbH“

---

## 📁 Projektstruktur

```bash
netbox-ip-diff-dashboard/
│
├── app.py                     # Flask-Frontend für Snapshot-Ansicht & Diff
├── daily.py                  # täglicher NetBox-API-Abzug (Cron geeignet)
├── netbox.py                 # API-Abfrage-Logik
├── netbox.db                 # SQLite-DB mit Snapshots & Diffs
│
├── templates/
│   ├── index.html            # Snapshot-Webansicht
│   └── diffs.html            # Diff-Webansicht
│
├── static/
│   ├── sentinex.css          # zentrales UI/CSS-Theme
│   └── logo-sentinex.svg     # Firmenlogo
│
├── venv/                     # Python virtualenv (nicht mitgitten!)
│
└── README.md                 # diese Datei
```

---

## ⚙️ Installation

### 1. Repository klonen

```bash
git clone https://github.com/dein-username/netbox-ip-diff-dashboard.git
cd netbox-ip-diff-dashboard
```

### 2. Python-Umgebung vorbereiten

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask requests
```

### 3. Locale aktivieren (für deutsches Datumsformat)

Falls du ein LXC- oder Minimal-Debian verwendest:

```bash
sudo locale-gen de_DE.UTF-8
```

Wird im Code zusätzlich mit `os.environ` abgesichert.

---

## 🧪 Snapshot manuell erzeugen

```bash
python3 daily.py
```

Empfohlen: täglicher Cronjob z. B.:

```cron
0 3 * * * /path/to/venv/bin/python3 /opt/netbox-ip-diff-dashboard/daily.py
```

---

## 🚀 Web-UI starten

```bash
python3 app.py
```

Dann im Browser aufrufen:

```
http://localhost:8000/
```

Optional Port angeben:

```bash
python3 app.py --port 8080
```

---

## 🌐 Beispielansicht

- 🔎 Filterleiste mit:
  - Dropdown (Tag)
  - Sucheingabefeld
- 📆 Aktuelles Snapshot-Datum oben in lesbarer Form:
  > „NetBox Snapshot – Stand vom 14. Mai 2025, 17:06 Uhr“
- 📋 Tabelle mit IP, Beschreibung, DNS und Tags
- 📉 Änderungen als Diff unter `/diffs`

---

## 🧾 Datenbankstruktur (SQLite)

### Tabelle `ip_records`

| Spalte         | Typ      | Beschreibung                 |
|----------------|----------|------------------------------|
| ip             | TEXT     | CIDR-formatiert              |
| description    | TEXT     | Beschreibung / Hostname      |
| dns_name       | TEXT     | DNS-Auflösung                |
| tags           | TEXT     | Python-Listen-String         |
| snapshot_date  | TEXT     | ISO-Timestamp (Datum)        |

### Tabelle `ip_diffs`

| Spalte         | Typ      | Beschreibung                 |
|----------------|----------|------------------------------|
| compare_date   | TEXT     | Vergleichsdatum (Snapshot)   |
| diff_json      | TEXT     | JSON mit hinzu/entfernt      |

---

## 🎨 Anpassbar per CSS

Bearbeite `static/sentinex.css` für:

- Farben (z. B. `.tag` für Badge-Style)
- Schriftgrößen
- Flexibles Responsive Design

---

## ❤️ Footer

Am Ende der Seite:

```html
<footer>
  <div class="footer-content">
    <span>Made with ❤️</span>
    <span>·</span>
    <span>The Leatherman</span>
    <span>·</span>
    <span>sentinex GmbH</span>
  </div>
</footer>
```

---

## 🛡️ ToDo / Roadmap

- [ ] CSV- / Excel-Export
- [ ] Light/Dark-Mode Toggle
- [ ] Auth (Basic Auth oder OIDC)
- [ ] Slack/Teams-Benachrichtigung bei Änderungen
- [ ] API-Endpoint zur Snapshot-Abfrage
- [ ] Monitoring-Integration (z. B. über Prometheus)

---

## 🧑‍💻 Entwickelt von

**Felix Cos** – Senior Network Engineer  
mit ❤️ bei **sentinex GmbH**  
→ „Built by The Leatherman.“
