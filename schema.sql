DROP TABLE IF EXISTS api_runs;

CREATE TABLE api_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    endpoint_tested TEXT,
    status_code INTEGER,
    latency_ms REAL,
    contrat_valide BOOLEAN,
    error_message TEXT
);
