CREATE TABLE algorithms (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    category    TEXT NOT NULL CHECK (category IN ('COMPRESSION', 'ENCRYPTION', 'STEGANOGRAPHY')),
    code        TEXT NOT NULL,
    enum_value  INTEGER,
    version     TEXT NOT NULL DEFAULT '1',
    description TEXT,
    is_active   INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    UNIQUE (category, code, version)
);

CREATE INDEX idx_algorithms_category ON algorithms(category, is_active);
