from app.core.bytes_tool import ByteWriter, ByteReader

from app.core.exceptions import NotOurImageFormatError
from app.core.image.image import (
    Compression,
    Encryption,
    ImageData,
    LSBImageData,
    LSBMetadata,
    PackingAlgorithm,
    PayloadMetadata, ChannelsMask,
)


class TextToImageSerializator:
    FORMAT_ID = b'T2IF'
    FORMAT_ID_SIZE = 4
    DATA_SIZE_SIZE = 4
    FILENAME_LEN_SIZE = 2
    COMPRESSION_SIZE = 1
    ENCRYPTION_SIZE = 1

    def serialize(self, image_data: ImageData) -> bytes:
        binary = ByteWriter()
        binary.write_bytes(self.FORMAT_ID)

        meta = image_data.meta
        if meta.filename is not None:
            binary.write_int(len(meta.filename.encode("utf-8")), self.FILENAME_LEN_SIZE)
            binary.write_str(meta.filename)
        else:
            binary.write_int(0, self.FILENAME_LEN_SIZE)

        binary.write_int(meta.size, self.DATA_SIZE_SIZE)
        binary.write_int(meta.compression.value, self.COMPRESSION_SIZE)
        binary.write_int(meta.encryption.value, self.ENCRYPTION_SIZE)
        binary.write_bytes(image_data.data)

        return binary.build()

    def deserialize(self, data: bytes) -> ImageData:
        reader = ByteReader(data)

        format_id = reader.read(self.FORMAT_ID_SIZE)
        if format_id != self.FORMAT_ID:
            raise NotOurImageFormatError("Invalid format id")

        filename_size = reader.read_int(self.FILENAME_LEN_SIZE)
        filename = reader.read_str(filename_size) if filename_size > 0 else None


        data_size = reader.read_int(self.DATA_SIZE_SIZE)
        if data_size <= 0:
            raise NotOurImageFormatError("Invalid data size")

        try:
            compression = Compression(reader.read_int(self.COMPRESSION_SIZE))
            encryption = Encryption(reader.read_int(self.ENCRYPTION_SIZE))
        except ValueError as e:
            raise NotOurImageFormatError("Invalid compression/encryption") from e

        payload = reader.read(data_size)

        meta = PayloadMetadata(
            size=data_size,
            filename=filename,
            compression=compression,
            encryption=encryption
        )

        return ImageData(meta=meta, data=payload)


class LSBSerializer:
    FORMAT_ID = b"LSB1"
    FORMAT_ID_SIZE = 4
    CHANNELS_MASK_SIZE = 1
    BITS_SIZE = 1
    DATA_SIZE_SIZE = 4
    COMPRESSION_SIZE = 1
    ENCRYPTION_SIZE = 1

    def serialize(self, image_data: LSBImageData) -> bytes:
        binary = ByteWriter()
        binary.write_bytes(self.FORMAT_ID)

        meta = image_data.meta
        binary.write_int(meta.channels_mask, self.CHANNELS_MASK_SIZE)
        binary.write_int(meta.bits_r, self.BITS_SIZE)
        binary.write_int(meta.bits_g, self.BITS_SIZE)
        binary.write_int(meta.bits_b, self.BITS_SIZE)
        binary.write_int(meta.bits_a, self.BITS_SIZE)
        binary.write_int(len(image_data.data), self.DATA_SIZE_SIZE)
        binary.write_int(meta.compression.value, self.COMPRESSION_SIZE)
        binary.write_int(meta.encryption.value, self.ENCRYPTION_SIZE)
        binary.write_bytes(image_data.data)

        return binary.build()

    def deserialize(self, data: bytes) -> LSBImageData:
        reader = ByteReader(data)

        format_id = reader.read(self.FORMAT_ID_SIZE)
        if format_id != self.FORMAT_ID:
            raise NotOurImageFormatError("Invalid LSB format id")

        channels_mask = reader.read_int(self.CHANNELS_MASK_SIZE)
        bits_r = reader.read_int(self.BITS_SIZE)
        bits_g = reader.read_int(self.BITS_SIZE)
        bits_b = reader.read_int(self.BITS_SIZE)
        bits_a = reader.read_int(self.BITS_SIZE)
        data_size = reader.read_int(self.DATA_SIZE_SIZE)

        if data_size <= 0:
            raise NotOurImageFormatError("Invalid LSB data size")

        try:
            channels_mask = ChannelsMask(channels_mask)
        except ValueError as e:
            raise NotOurImageFormatError("Invalid LSB channels mask") from e
        try:
            compression = Compression(reader.read_int(self.COMPRESSION_SIZE))
            encryption = Encryption(reader.read_int(self.ENCRYPTION_SIZE))
        except ValueError as e:
            raise NotOurImageFormatError("Invalid LSB compression/encryption") from e

        payload = reader.read(data_size)
        if len(payload) != data_size:
            raise NotOurImageFormatError("Unexpected end of LSB payload")

        meta = LSBMetadata(
            channels_mask=channels_mask,
            bits_r=bits_r,
            bits_g=bits_g,
            bits_b=bits_b,
            bits_a=bits_a,
            size=data_size,
            compression=compression,
            encryption=encryption,
        )

        return LSBImageData(meta=meta, data=payload)
