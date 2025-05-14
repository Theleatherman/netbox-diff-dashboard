CREATE TABLE IF NOT EXISTS ip_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_date TEXT,
    ip TEXT,
    description TEXT,
    dns_name TEXT,
    tags TEXT
);

CREATE TABLE IF NOT EXISTS ip_diffs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    compare_date TEXT,
    diff_json TEXT
);
