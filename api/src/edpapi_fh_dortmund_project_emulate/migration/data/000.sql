CREATE TABLE IF NOT EXISTS seqam_fh_dortmund_project_emulate.metrics (
    host String,
    time DateTime,
    state String
) ENGINE = MergeTree PRIMARY KEY (host, time)
ORDER BY (host, time)
TTL time + INTERVAL 1 MONTH DELETE
