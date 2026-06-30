CREATE TABLE images (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_user_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_image_id INTEGER REFERENCES images(id) ON DELETE SET NULL,
    file_path       TEXT NOT NULL,
    original_name   TEXT,
    image_format    TEXT NOT NULL,
    channels_mask   TEXT CHECK (channels_mask IN ('RGB', 'RGBA')),
    width_px        INTEGER,
    height_px       INTEGER,
    file_size_bytes INTEGER NOT NULL,
    sha256_hash     TEXT NOT NULL,
    is_stego        INTEGER NOT NULL DEFAULT 0 CHECK (is_stego IN (0, 1)),
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_images_owner  ON images(owner_user_id);
CREATE INDEX idx_images_source ON images(source_image_id);
CREATE INDEX idx_images_hash   ON images(sha256_hash);
