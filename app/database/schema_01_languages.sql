CREATE TABLE languages (
    code        TEXT PRIMARY KEY,
    name_native TEXT NOT NULL,
    name_en     TEXT NOT NULL,
    is_active   INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);
