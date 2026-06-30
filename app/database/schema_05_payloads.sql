CREATE TABLE payloads (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id              INTEGER NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    payload_type          TEXT NOT NULL CHECK (payload_type IN ('TEXT', 'FILE')),
    original_filename     TEXT,
    mime_type             TEXT,
    original_size_bytes   INTEGER NOT NULL,
    embedded_size_bytes   INTEGER NOT NULL,
    packing_algorithm     TEXT NOT NULL CHECK (packing_algorithm IN ('RGB', 'LSB')),
    compression_code      TEXT NOT NULL CHECK (compression_code IN ('NONE', 'ZLIB', 'GZIP')),
    encryption_code       TEXT NOT NULL CHECK (encryption_code IN ('NONE', 'XOR', 'ChaCha20')),
    lsb_channels_mask     TEXT CHECK (lsb_channels_mask IN ('RGB', 'RGBA')),
    lsb_bits_r            INTEGER,
    lsb_bits_g            INTEGER,
    lsb_bits_b            INTEGER,
    lsb_bits_a            INTEGER,
    checksum_sha256       TEXT NOT NULL,
    created_at            TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_payloads_image ON payloads(image_id);
