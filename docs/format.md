## Binary Image Format

# Structure

|                     |  Type   | Size (bytes) | Description                              |
|:--------------------|:-------:|:------------:|:-----------------------------------------|
| **format_id**       |  `str`  |      4       | Signature for format identification      |
| **filename_length** |  `int`  |      1       | File name length                         |
| **filename**        |  `str`  | filename_len | File name in UTF-8 (If filename_len > 0) |
| **data_size**       |  `int`  |      4       | Payload size in bytes                    |
| **compression**     |  `int`  |      1       | Compression alghorythm id                |
| **encryption**      |  `int`  |      1       | Encryption alghorythm id                 |
| **nonce**           | `bytes` |      12      | Nonce for encryption(if ChaCha20)        |
| **payload**         | `bytes` |  data_size   | Binary data                              |

# Compression

| ID | Alghorythm | Description      |
|:--:|:----------:|:-----------------|
| 0  |    None    | No compression   |
| 1  |    Zlib    | Zlib compression |
| 2  |    Gzip    | Gzip compression |

# Encryption

| ID | Alghorythm | Description    |
|:--:|:----------:|:---------------|
| 0  |    None    | No encryption  |
| 1  |    XOR     | XOR encryption |
| 2  |  ChaCha20  | ChaCha20       |