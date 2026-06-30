class LSBFormat:
    FORMAT_ID = b"LSB1"

    FORMAT_ID_SIZE = 4
    CHANNELS_MASK_SIZE = 1
    BITS_SIZE = 1
    DATA_SIZE_SIZE = 4
    COMPRESSION_SIZE = 1
    ENCRYPTION_SIZE = 1

    HEADER_SIZE = (
            FORMAT_ID_SIZE
            + CHANNELS_MASK_SIZE
            + BITS_SIZE * 3  # r, g, b
            + DATA_SIZE_SIZE
            + COMPRESSION_SIZE
            + ENCRYPTION_SIZE
    )

    BOOTSTRAP_RED_BITS = 1
    BOOTSTRAP_GREEN_BITS = 1
    BOOTSTRAP_BLUE_BITS = 1
