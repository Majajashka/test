from app.core.bytes_tool import ByteWriter, ByteReader

from app.core.exceptions import NotOurImageFormatError
from app.core.image.formats.lsb import LSBFormat
from app.core.image.formats.t2i import T2IFFormat
from app.core.image.image import (
    Compression,
    Encryption,
    ImageData,
    LSBImageData,
    LSBMetadata,
    PayloadMetadata, ChannelsMask,
)


class TextToImageSerializator:

    @staticmethod
    def serialize(image_data: ImageData) -> bytes:
        binary = ByteWriter()
        binary.write_bytes(T2IFFormat.FORMAT_ID)

        meta = image_data.meta

        binary.write_int(meta.size, T2IFFormat.DATA_SIZE_SIZE)
        binary.write_int(meta.compression.value, T2IFFormat.COMPRESSION_SIZE)
        binary.write_int(meta.encryption.value, T2IFFormat.ENCRYPTION_SIZE)
        binary.write_bytes(image_data.data)

        return binary.build()

    @staticmethod
    def deserialize(data: bytes) -> ImageData:
        reader = ByteReader(data)

        format_id = reader.read(T2IFFormat.FORMAT_ID_SIZE)
        if format_id != T2IFFormat.FORMAT_ID:
            raise NotOurImageFormatError("Invalid format id")

        data_size = reader.read_int(T2IFFormat.DATA_SIZE_SIZE)
        if data_size <= 0:
            raise NotOurImageFormatError("Invalid data size")

        try:
            compression = Compression(reader.read_int(T2IFFormat.COMPRESSION_SIZE))
            encryption = Encryption(reader.read_int(T2IFFormat.ENCRYPTION_SIZE))
        except ValueError as e:
            raise NotOurImageFormatError("Invalid compression/encryption") from e

        payload = reader.read(data_size)

        meta = PayloadMetadata(
            size=data_size,
            compression=compression,
            encryption=encryption
        )

        return ImageData(meta=meta, data=payload)


class LSBSerializer:

    @staticmethod
    def serialize(image_data: LSBImageData) -> bytes:
        binary = ByteWriter()
        binary.write_bytes(LSBFormat.FORMAT_ID)

        meta = image_data.meta
        binary.write_int(meta.channels_mask, LSBFormat.CHANNELS_MASK_SIZE)
        binary.write_int(meta.bits_r, LSBFormat.BITS_SIZE)
        binary.write_int(meta.bits_g, LSBFormat.BITS_SIZE)
        binary.write_int(meta.bits_b, LSBFormat.BITS_SIZE)
        binary.write_int(len(image_data.data), LSBFormat.DATA_SIZE_SIZE)
        binary.write_int(meta.compression.value, LSBFormat.COMPRESSION_SIZE)
        binary.write_int(meta.encryption.value, LSBFormat.ENCRYPTION_SIZE)
        binary.write_bytes(image_data.data)

        return binary.build()

    @staticmethod
    def deserialize(data: bytes) -> LSBImageData:
        reader = ByteReader(data)

        format_id = reader.read(LSBFormat.FORMAT_ID_SIZE)
        if format_id != LSBFormat.FORMAT_ID:
            raise NotOurImageFormatError("Invalid LSB format id")

        channels_mask = reader.read_int(LSBFormat.CHANNELS_MASK_SIZE)
        bits_r = reader.read_int(LSBFormat.BITS_SIZE)
        bits_g = reader.read_int(LSBFormat.BITS_SIZE)
        bits_b = reader.read_int(LSBFormat.BITS_SIZE)
        data_size = reader.read_int(LSBFormat.DATA_SIZE_SIZE)

        if data_size <= 0:
            raise NotOurImageFormatError("Invalid LSB data size")

        try:
            channels_mask = ChannelsMask(channels_mask)
        except ValueError as e:
            raise NotOurImageFormatError("Invalid LSB channels mask") from e
        try:
            compression = Compression(reader.read_int(LSBFormat.COMPRESSION_SIZE))
            encryption = Encryption(reader.read_int(LSBFormat.ENCRYPTION_SIZE))
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
            size=data_size,
            compression=compression,
            encryption=encryption,
        )

        return LSBImageData(meta=meta, data=payload)

    @staticmethod
    def deserialize_meta(data: bytes) -> LSBMetadata:
        reader = ByteReader(data)

        format_id = reader.read(LSBFormat.FORMAT_ID_SIZE)
        if format_id != LSBFormat.FORMAT_ID:
            raise NotOurImageFormatError(f"Invalid LSB format id - {format_id}")

        channels_mask = reader.read_int(LSBFormat.CHANNELS_MASK_SIZE)
        bits_r = reader.read_int(LSBFormat.BITS_SIZE)
        bits_g = reader.read_int(LSBFormat.BITS_SIZE)
        bits_b = reader.read_int(LSBFormat.BITS_SIZE)
        data_size = reader.read_int(LSBFormat.DATA_SIZE_SIZE)

        if data_size <= 0:
            raise NotOurImageFormatError("Invalid LSB data size")

        try:
            channels_mask = ChannelsMask(channels_mask)
        except ValueError as e:
            raise NotOurImageFormatError("Invalid LSB channels mask") from e
        try:
            compression = Compression(reader.read_int(LSBFormat.COMPRESSION_SIZE))
            encryption = Encryption(reader.read_int(LSBFormat.ENCRYPTION_SIZE))
        except ValueError as e:
            raise NotOurImageFormatError("Invalid LSB compression/encryption") from e

        meta = LSBMetadata(
            channels_mask=channels_mask,
            bits_r=bits_r,
            bits_g=bits_g,
            bits_b=bits_b,
            size=data_size,
            compression=compression,
            encryption=encryption,
        )

        return meta
