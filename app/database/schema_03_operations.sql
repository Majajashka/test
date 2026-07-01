CREATE TABLE operations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    operation_type  TEXT NOT NULL CHECK (operation_type IN ('EMBED', 'EXTRACT')),
    status          TEXT NOT NULL CHECK (status IN ('SUCCESS', 'FAILED')),
    error_message   TEXT,
    duration_ms     INTEGER,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_operations_user    ON operations(user_id);
CREATE INDEX idx_operations_created ON operations(created_at);
