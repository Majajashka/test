from app.core.bytes_tool import ByteWriter, ByteReader

from app.core.exceptions import NotOurImageFormatError
from app.core.image.image import ImageData, PayloadMetadata, Encryption, Compression


class BinaryImageSerializer:
    FORMAT_ID = b'BIMG'
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

        data_size = reader.read_int(self.DATA_SIZE_SIZE)
        if data_size <= 0:
            raise NotOurImageFormatError("Invalid data size")

        filename_size = reader.read_int(self.FILENAME_LEN_SIZE)
        filename = reader.read_str(filename_size) if filename_size > 0 else None

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


