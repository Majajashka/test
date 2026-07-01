from dataclasses import dataclass
from pathlib import Path

from app.core.compression import CompressorFactory
from app.core.crypto.cipher import CipherFactory
from app.core.crypto.hasher import PasswordHasher
from app.core.image.image import Compression, Encryption, ImageData, PayloadMetadata
from app.core.image.packers.raw_rgb import RGBImagePacker, RGBImageUnpacker
from app.core.image.serializers import TextToImageSerializator
from app.database.image_repository import ImageRepository
from app.database.transaction_manager import TransactionManager


@dataclass
class PackDataResult:
    image_id: int
    user_id: int


class PackTextToImageInteractor:

    def __init__(
            self,
            image_repo: ImageRepository,
            transaction_manager: TransactionManager,
            rgb_packer: RGBImagePacker,
            serializer: TextToImageSerializator,
            cipher_factory: CipherFactory,
            compressor_factory: CompressorFactory,
            password_hasher: PasswordHasher
    ):
        self.image_repo = image_repo
        self.transaction_manager = transaction_manager
        self.packer = rgb_packer
        self.serializer = serializer
        self.cipher_factory = cipher_factory
        self.compressor_factory = compressor_factory
        self.password_hasher = password_hasher

    def execute(
            self,
            text: str,
            path_to_save: Path,
            compression: Compression,
            encryption: Encryption,
            user_id: int,
            password: str | None = None
    ) -> PackDataResult:
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

        serialized_data = self.serializer.serialize(
            image_data=ImageData(
                meta=PayloadMetadata(
                    size=len(text_in_bytes),
                    compression=compression,
                    encryption=encryption
                ),
                data=text_in_bytes
            )
        )
        result = self.packer.pack(serialized_data, path_to_save)
        with self.transaction_manager:
            img_id = self.image_repo.create_image(
                owner_user_id=user_id,
                file_path=str(path_to_save),
                image_format="PNG",
                channels_mask="RGB",
                file_size_bytes=result.size,
                sha256_hash=result.sha256,
                width_px=result.width,
                height_px=result.height,
                is_stego=False
            )

            self.transaction_manager.commit()

        return PackDataResult(image_id=img_id, user_id=user_id)


class UnpackImageToTextInteractor:

    def __init__(
            self,
            serializer: TextToImageSerializator,
            cipher_factory: CipherFactory,
            compressor_factory: CompressorFactory,
            password_hasher: PasswordHasher,
            unpacker: RGBImageUnpacker,
    ):
        self.unpacker = unpacker
        self.serializer = serializer
        self.cipher_factory = cipher_factory
        self.compressor_factory = compressor_factory
        self.password_hasher = password_hasher

    def execute(self, path_to_image: Path, password: str | None = None) -> str:
        raw_data = self.unpacker.unpack(path_to_image)
        image_data = self.serializer.deserialize(raw_data)
        data = image_data.data

        if image_data.meta.encryption != Encryption.NONE:
            if password is None:
                raise ValueError("Password is required for decryption.")
            cipher = self.cipher_factory.get_cipher(image_data.meta.encryption)
            data = cipher.decrypt(
                data=data,
                key=self.password_hasher.hash(password)
            )
        if image_data.meta.compression != Compression.NONE:
            compressor = self.compressor_factory.get_compressor(image_data.meta.compression)
            data = compressor.decompress(data)

        return data.decode("utf-8")
