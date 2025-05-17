# 🛰️ NetBox IP Diff Dashboard

Ein schlankes, CI-konformes Dashboard zur täglichen Auswertung von IP-Daten aus der NetBox-API.  
Visualisiert IP-Zustände, ermöglicht Tag-Filter, Volltextsuche, Differenzvergleiche zwischen Snapshots und bietet ein modernes Webfrontend im Sentinex-Stil.

---

## 📦 Features

- 🔁 **Täglicher Snapshot** aller IP-Adressen aus NetBox mit Beschreibung/DNS/Tags
- 🕵️ **Filterung nach Tags** (dynamisch, „mgmt-if“ wird automatisch ausgeblendet)
- 🔍 **Volltextsuche** über IP, Beschreibung & DNS
- 📊 **DataTables-Integration** für Sortierung, Pagination & Suche
- 🏷️ Tags in Badge-Optik, an NetBox UI angelehnt
- 🧠 Automatische **Diff-Berechnung zwischen Snapshots**
- 🌙 **Dark Mode UI** im Sentinex-Design (anpassbar per CSS)
- 🧾 **Responsive** für Tablets / kleine Displays
- 💬 Lokalisierung in Deutsch
- 📥 SQLite-basiertes Datenlog
- ❤️ Footer: „Made with ❤️ by The Leatherman | sentinex GmbH“
- 📤 Exportfunktionen für CSV & Excel
- 🧠 Snapshot-Vergleich via Web + E-Mail mit HTML-Template
- 🧭 Navigation mit aktiver Seitenmarkierung & Font Awesome Icons
- ✨ Pulsierender NetBox-Logoeffekt im UI (hover-responsive)

---

## 📁 Projektstruktur

```bash
netbox-ip-diff-dashboard/
│
├── app.py                     # Flask-Frontend für Snapshot-Ansicht & Diff
├── daily.py                  # täglicher NetBox-API-Abzug (Cron geeignet)
├── netbox.py                 # API-Abfrage-Logik
├── emailer.py                # HTML-E-Mail-Versand für Snapshot-Diffs
├── netbox.db                 # SQLite-DB mit Snapshots & Diffs
│
├── templates/
│   ├── index.html            # Snapshot-Webansicht
│   ├── diffs.html            # Änderungsansicht (Diffs)
│   ├── snapshots.html        # Rohdaten-Tabellenansicht
│   ├── home.html             # Startseite mit Logo & Navigation
│   └── base.html             # zentrales Layout inkl. Navigation
│
├── static/
│   ├── sentinex.css          # zentrales UI/CSS-Theme inkl. Logoeffekt
│   ├── sentinex-s-w.png      # Navigationslogo (weiß)
│   ├── net-graphic.png       # Dashboard-Titelgrafik
│   └── favicon.png           # Website-Icon
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
pip install flask requests babel
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
0 6 * * * /opt/netbox-ip-diff-dashboard/venv/bin/python3 /opt/netbox-ip-diff-dashboard/daily.py >> /var/log/netbox-diff.log 2>&1
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

## 🔁 systemd + Cron Integration

### Systemd-Service:

```ini
[Unit]
Description=NetBox Dashboard
After=network.target

[Service]
ExecStart=/opt/netbox-ip-diff-dashboard/venv/bin/python3 /opt/netbox-ip-diff-dashboard/app.py
WorkingDirectory=/opt/netbox-ip-diff-dashboard
Restart=always
Environment=FLASK_ENV=production
User=root

[Install]
WantedBy=multi-user.target
```

### Aktivieren:
```bash
sudo systemctl enable --now netbox-dashboard.service
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
- Schriftgrößen, Fonts, Hovereffekte
- Logo-Animationen (hover, pulsierend)

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
    <span>·</span>
    <span>{{ year }}</span>
  </div>
</footer>
```

---

## 🛡️ ToDo / Roadmap

- [x] CSV- / Excel-Export mit sichtbaren Zeilen
- [x] Snapshot-Zeitstempel human-readable + sortierbar
- [x] Font Awesome Icons statt Emojis
- [x] Animated NetBox-Logo (hover)
- [ ] Auth (Basic Auth oder OIDC)
- [ ] API-Endpoint zur Snapshot-Abfrage
- [ ] Monitoring-Integration (Prometheus)
- [ ] Slack/Teams-Benachrichtigung bei Änderungen
- [ ] Light/Dark-Mode Toggle

---

## 🧑‍💻 Entwickelt von

**Felix Cos** – Senior Network Engineer  
mit ❤️ bei **sentinex GmbH**  
→ „Built by The Leatherman.“
