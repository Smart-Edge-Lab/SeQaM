CREATE TABLE IF NOT EXISTS seqam_fh_dortmund_project_emulate.cpu_load (
    host String,
    time DateTime,
    core UInt8,
    load Float32
) ENGINE = MergeTree PRIMARY KEY (host, time)
ORDER BY (host, time)
TTL time + INTERVAL 1 MONTH DELETE
