# T2IF (RGB container)

|                     |  Type   | Size (bytes) | Description                               |
|:--------------------|:-------:|:------------:|:------------------------------------------|
| **format_id**       | `bytes` |      4       | Signature `"T2IF"`                        |
| **filename_length** |  `int`  |      2       | File name length                          |
| **filename**        |  `str`  | filename_len | File name in UTF-8 (if filename_len > 0)  |
| **data_size**       |  `int`  |      4       | Payload size in bytes                     |
| **compression**     |  `int`  |      1       | Compression algorithm id                  |
| **encryption**      |  `int`  |      1       | Encryption algorithm id                   |
| **payload**         | `bytes` |  data_size   | Binary data (nonce included for ChaCha20) |

# LSB (steganography)

| Field             | Type    | Size | Description                               |
|-------------------|---------|------|-------------------------------------------|
| **format_id**     | `bytes` | 4    | Signature `"LSB1"`                        |
| **channels_mask** | `int`   | 1    | Bitmask(RGB)                              |
| **bits_r**        | `int`   | 1    | Bits per R channel                        |
| **bits_g**        | `int`   | 1    | Bits per G channel                        |
| **bits_b**        | `int`   | 1    | Bits per B channel                        |
| **data_size**     | `int`   | 4    | Payload size in bytes                     |
| **compression**   | `int`   | 1    | Compression algorithm id                  |
| **encryption**    | `int`   | 1    | Encryption algorithm id                   |
| **payload**       | `bytes` | N    | Binary data (nonce included for ChaCha20) |

# Packing algorithm

| ID | Algorithm | Description       |
|:--:|:---------:|:------------------|
| 1  |    RGB    | Raw RGB container |
| 2  |    LSB    | LSB steganography |

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

# Channels mask

| ID | Alghorythm | Description |
|:--:|:----------:|:------------|
| 0  |    RGB     | RGB         |
