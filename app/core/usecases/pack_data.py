from pathlib import Path

from app.core.compression import CompressorFactory
from app.core.crypto.cipher import CipherFactory
from app.core.crypto.hasher import PasswordHasher
from app.core.image.image import Compression, Encryption, ImageData, PayloadMetadata
from app.core.image.reader import ImageWriter, ImageReader
from app.core.image.serializers import TextToImageSerializator


class PackTextToImageInteractor:

    def __init__(
            self,
            serializer: TextToImageSerializator,
            writer: ImageWriter,
            cipher_factory: CipherFactory,
            compressor_factory: CompressorFactory,
            password_hasher: PasswordHasher
    ):
        self.serializer = serializer
        self.writer = writer
        self.cipher_factory = cipher_factory
        self.compressor_factory = compressor_factory
        self.password_hasher = password_hasher

    def execute(
            self,
            text: str,
            path_to_save: Path,
            compression: Compression,
            encryption: Encryption,
            password: str | None = None
    ) -> None:
        if password is None and encryption != Encryption.NONE:
            raise ValueError("Password is required for encryption.")

        text_in_bytes = text.encode("utf-8")

        if compression != Compression.NONE:
            compressor = self.compressor_factory.get_compressor(compression)
            text_in_bytes = compressor.compress(text_in_bytes)

        if encryption != Encryption.NONE:
            cipher = self.cipher_factory.get_cipher(encryption)
            text_in_bytes = cipher.encrypt(
                data=text_in_bytes,
                key=self.password_hasher.hash(password)
            )

        image_data = self.serializer.serialize(
            image_data=ImageData(
                meta=PayloadMetadata(
                    size=len(text_in_bytes),
                    filename=None,
                    compression=compression,
                    encryption=encryption
                ),
                data=text_in_bytes
            )
        )
        self.writer.write(data=image_data, path=path_to_save)


class UnpackImageToTextInteractor:

    def __init__(
            self, serializer: TextToImageSerializator, cipher_factory: CipherFactory,
            compressor_factory: CompressorFactory, reader: ImageReader, password_hasher: PasswordHasher
            ):
        self.serializer = serializer
        self.cipher_factory = cipher_factory
        self.compressor_factory = compressor_factory
        self.reader = reader
        self.password_hasher = password_hasher

    def execute(self, path_to_image: Path, password: str | None = None) -> str:
        raw_data = self.reader.read_bytes(path_to_image)
        image_data = self.serializer.deserialize(raw_data)

        if image_data.meta.encryption != Encryption.NONE:
            if password is None:
                raise ValueError("Password is required for decryption.")
            cipher = self.cipher_factory.get_cipher(image_data.meta.encryption)
            image_data = cipher.decrypt(
                data=image_data.data,
                key=self.password_hasher.hash(password)
            )

        if image_data.meta.compression != Compression.NONE:
            compressor = self.compressor_factory.get_compressor(image_data.meta.compression)
            image_data = compressor.decompress(image_data.data)

        return image_data.decode("utf-8")
