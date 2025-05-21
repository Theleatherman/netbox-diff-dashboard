# 🛰️ NetBox IP Diff Dashboard

Ein schlankes, CI-konformes Dashboard zur täglichen Auswertung von IP-Daten aus der NetBox-API.  
Visualisiert IP-Zustände, ermöglicht Tag-Filter, Volltextsuche, Differenzvergleiche zwischen Snapshots und bietet ein modernes Webfrontend im Sentinex-Stil.

---

## 📦 Features

- 🔁 **Täglicher Snapshot** aller IP-Adressen aus NetBox mit Beschreibung/DNS/Tags
- 🕵️ **Filterung nach Tags** (dynamisch, „mgmt-if“ wird automatisch ausgeblendet)
- 🔍 **Volltextsuche** über IP, Beschreibung & DNS
- 📊 **DataTables-Integration** für Sortierung, Pagination & Suche
- 📤 **CSV- und Excel-Export** über Button
- 🧠 Automatische **Diff-Berechnung zwischen Snapshots** (inkl. farblich differenzierter Tabellen)
- 💌 **HTML-E-Mail-Benachrichtigung** bei Änderungen (inkl. `emailer.py`)
- 📅 **Snapshot-Cleanup-Script** (`clean_bad_snapshots.py`)
- 🧭 Navigation mit aktiver Seitenmarkierung und **Font Awesome Icons**
- ✨ Hover-basierter, leicht pulsierender Effekt am **NetBox-Logo**
- 🌙 **Dark Mode UI** im Sentinex-Design (anpassbar per CSS)
- 🧾 **Responsive** für Tablets / kleine Displays
- 🔐 **OAuth2 (Okta) Login** via `oauth2-proxy`
- 🌐 **Reverse Proxy / HTTPS / Auth** via nginx
- 💬 Lokalisierung in Deutsch
- 📥 SQLite-basiertes Datenlog (`netbox.db`)
- ❤️ Footer: „Made with ❤️ by The Leatherman | sentinex GmbH“

---

## 📁 Projektstruktur

```bash
netbox-ip-diff-dashboard/
│
├── app.py                        # Flask-Frontend (Home, Snapshots, Diffs)
├── daily.py                      # täglicher Snapshot + Diff-Bildung + E-Mail
├── netbox.py                     # NetBox-API-Abfrage (authentifiziert, gefiltert)
├── emailer.py                    # HTML-Mail-Renderer für Diff-Benachrichtigung
├── config.py                     # zentrale Konfig (u. a. SMTP)
├── diffing.py                    # Kernlogik zum Vergleich der Snapshots
├── db.py                         # DB-Hilfsfunktionen
├── clean_bad_snapshots.py        # Bereinigt Snapshots mit leerem Inhalt
│
├── nginx/
│   └── netbox-diff.conf          # nginx-Site mit SSL & OAuth2-Proxy
│
├── oauth2-proxy/
│   └── oauth2-proxy.cfg          # Konfig für Okta + Upstream-Proxypass
│
├── static/
│   ├── sentinex.css              # CI-Design / Dark Theme / Logo-Effekt
│   ├── sentinex-s-w.png          # Navigationslogo (weiß)
│   ├── netbox_logo.svg           # pulsierendes Dashboard-Logo
│   ├── netbox-light-favicon.png  # Favicon hell
│   ├── apple-icon.png            # Apple Touch Icon
│   └── favicon.png               # Browser-Favicon
│
├── templates/
│   ├── base.html                 # zentrales Layout + Navigation
│   ├── home.html                 # Startseite (Dashboard + Links)
│   ├── index.html                # Snapshot-Ansicht mit Filter
│   ├── diffs.html                # Änderungsübersicht
│   ├── snapshots.html            # Tabellenansicht (raw)
│   ├── template.html             # HTML-Vorlage für E-Mail
│   └── test-mail.py              # Mailversandtest (Debug)
│
├── netbox.db                     # SQLite-Datenbank (Snapshots & Diffs)
├── logs_cli.py                   # Snapshots/Logs für Debug (CLI-basiert)
├── report.html                   # statisches HTML-Diff-Report-Demo
├── requirements.txt              # Python-Abhängigkeiten
├── schema.sql                    # optionaler SQL-Dump
│
├── .env                          # Umgebungsvariablen (z. B. SMTP)
├── .gitignore
├── LICENSE
└── README.md                     # diese Datei
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

## 🔐 Reverse Proxy mit HTTPS & Okta Authentifizierung

### 1. nginx installieren

```bash
sudo apt update
sudo apt install nginx
```

---

### 2. SSL-Zertifikat bereitstellen

Zertifikatsdateien in folgende Pfade ablegen:

```bash
/etc/ssl/certs/wildcard_avemo-group_net.crt
/etc/ssl/private/wildcard_avemo-group_net.key
```

Dateiberechtigungen absichern:

```bash
chmod 600 /etc/ssl/private/wildcard_avemo-group_net.key
```

---

### 3. nginx als Reverse Proxy konfigurieren

```nginx
server {
    listen 443 ssl;
    server_name netbox-diff.avemo-group.net;

    ssl_certificate     /etc/ssl/certs/wildcard_avemo-group_net.crt;
    ssl_certificate_key /etc/ssl/private/wildcard_avemo-group_net.key;

    location /oauth2/ {
        proxy_pass http://localhost:4180;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        auth_request /oauth2/auth;
        error_page 401 = /oauth2/start;

        proxy_pass http://localhost:4180;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Aktivieren & neustarten:

```bash
sudo systemctl reload nginx
```

---

### 4. OAuth2-Proxy herunterladen & entpacken

```bash
cd /opt
wget https://github.com/oauth2-proxy/oauth2-proxy/releases/download/v7.9.0/oauth2-proxy-v7.9.0.linux-amd64.tar.gz
tar -xvzf oauth2-proxy-v7.9.0.linux-amd64.tar.gz
mv oauth2-proxy-v7.9.0.linux-amd64 oauth2-proxy
chmod +x /opt/oauth2-proxy/oauth2-proxy
```

---

### 5. Konfiguration erstellen unter `/etc/oauth2-proxy.cfg`

Zunächst das cookie_secret generieren:
```bash
head -c32 /dev/urandom | base64
```

```ini
provider = "oidc"
redirect_url = "https://netbox-diff.avemo-group.net/oauth2/callback"
oidc_issuer_url = "https://login.avemo-it.cloud/oauth2/default"
upstreams = [ "http://127.0.0.1:8000" ]
email_domains = [ "*" ]

client_id = "OKTA_CLIENT_ID"
client_secret = "OKTA_CLIENT_SECRET"

cookie_secret = "BASE64_32_BYTE_SECRET"
cookie_secure = true
skip_provider_button = true
pass_access_token = true
```

> Ersetze `OKTA_CLIENT_ID`, `OKTA_CLIENT_SECRET` und `cookie_secret` entsprechend deinen Werten.

---

### 6. Systemd-Service für OAuth2-Proxy

```ini
# /etc/systemd/system/oauth2-proxy.service

[Unit]
Description=OAuth2 Proxy for NetBox Diff Dashboard
After=network.target

[Service]
ExecStart=/opt/oauth2-proxy/oauth2-proxy --config /etc/oauth2-proxy.cfg
WorkingDirectory=/opt
Restart=always
User=root

[Install]
WantedBy=multi-user.target
```

Aktivieren & starten:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now oauth2-proxy.service
```

---

### 7. Testzugriff

- Aufrufen: `https://netbox-diff.avemo-group.net`
- Login erfolgt über Okta
- Nach erfolgreicher Authentifizierung erfolgt Weiterleitung zum Dashboard

> Alle Requests an `/` sind nun durch OAuth2-Login via Okta geschützt.

---

## 🛡️ ToDo / Roadmap

- [x] CSV- / Excel-Export mit sichtbaren Zeilen
- [x] Snapshot-Zeitstempel human-readable + sortierbar
- [x] Font Awesome Icons statt Emojis
- [x] Animated NetBox-Logo (hover)
- [x] HTTPS mit wildcard-Zertifkat
- [x] Auth (Basic Auth oder OIDC)
- [ ] API-Endpoint zur Snapshot-Abfrage
- [ ] Monitoring-Integration (Prometheus)
- [ ] Slack/Teams-Benachrichtigung bei Änderungen
- [ ] Light/Dark-Mode Toggle

---

## 🧑‍💻 Entwickelt von

**Felix Cos** – Senior Network Engineer  
mit ❤️ bei **sentinex GmbH**  
→ „Built by The Leatherman.“
