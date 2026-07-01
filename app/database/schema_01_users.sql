CREATE TABLE users (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    username            TEXT NOT NULL UNIQUE,
    password_hash       TEXT NOT NULL,
    password_algo       TEXT NOT NULL DEFAULT 'pbkdf2_sha256',
    password_salt       TEXT,
    preferred_lang_code TEXT NOT NULL DEFAULT 'ka' CHECK (preferred_lang_code IN ('ka', 'en', 'ru')),
    is_active           INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    last_login_at       TEXT
);

CREATE INDEX idx_users_username ON users(username);
