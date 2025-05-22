
-- Erweiterung um DNS-Caching
CREATE TABLE IF NOT EXISTS dns_cache (
    ip TEXT PRIMARY KEY,
    hostname TEXT,
    zone TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
