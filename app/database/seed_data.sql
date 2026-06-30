INSERT INTO languages (code, name_native, name_en) VALUES
    ('ka', 'ქართული', 'Georgian'),
    ('en', 'English', 'English'),
    ('ru', 'Русский', 'Russian');

INSERT INTO algorithms (category, code, enum_value, version, description) VALUES
    ('COMPRESSION', 'NONE', 0, '1', NULL),
    ('COMPRESSION', 'ZLIB', 1, '1', NULL),
    ('COMPRESSION', 'GZIP', 2, '1', NULL);

INSERT INTO algorithms (category, code, enum_value, version, description) VALUES
    ('ENCRYPTION', 'NONE', 0, '1', NULL),
    ('ENCRYPTION', 'XOR', 1, '1', NULL),
    ('ENCRYPTION', 'ChaCha20', 2, '1', NULL);

INSERT INTO algorithms (category, code, enum_value, version, description) VALUES
    ('STEGANOGRAPHY', 'RGB', 1, '1', NULL),
    ('STEGANOGRAPHY', 'LSB', 2, '1', NULL);
