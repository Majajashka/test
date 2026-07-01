from pathlib import Path

from app.core.compression import CompressorFactory
from app.core.crypto.cipher import CipherFactory
from app.core.crypto.hasher import PasswordHasher
from app.core.image.image import Compression, Encryption, LSBImageData, LSBMetadata
from app.core.image.packers.lsb import LSBImagePacker, LSBImageUnpacker
from app.core.image.serializers import LSBSerializer
from app.database.image_repository import ImageRepository
from app.database.transaction_manager import TransactionManager


class PackTextToLSBImageInteractor:

    def __init__(
            self,
            image_repo: ImageRepository,
            transaction_manager: TransactionManager,
            serializer: LSBSerializer,
            packer: LSBImagePacker,
            cipher_factory: CipherFactory,
            compressor_factory: CompressorFactory,
            password_hasher: PasswordHasher,
    ):
        self.image_repo = image_repo
        self.transaction_manager = transaction_manager
        self.serializer = serializer
        self.packer = packer
        self.cipher_factory = cipher_factory
        self.compressor_factory = compressor_factory
        self.password_hasher = password_hasher

    def execute(
            self,
            text: str,
            source_path: Path,
            path_to_save: Path,
            compression: Compression,
            encryption: Encryption,
            user_id: int,
            password: str | None = None,
    ) -> None:
        if password is None and encryption != Encryption.NONE:
            raise ValueError("Password is required for encryption.")

        payload = text.encode("utf-8")

        if compression != Compression.NONE:
            compressor = self.compressor_factory.get_compressor(compression)
            payload = compressor.compress(payload)

        if encryption != Encryption.NONE:
            cipher = self.cipher_factory.get_cipher(encryption)
            payload = cipher.encrypt(
                data=payload,
                key=self.password_hasher.hash(password),
            )

        config = self.packer.config
        serialized = self.serializer.serialize(
            image_data=LSBImageData(
                meta=LSBMetadata(
                    channels_mask=self.packer.image_reader.mode,
                    bits_r=config.red_bits,
                    bits_g=config.green_bits,
                    bits_b=config.blue_bits,
                    size=len(payload),
                    compression=compression,
                    encryption=encryption,
                ),
                data=payload,
            )
        )

        result = self.packer.pack(
            data=serialized, source_image_path=source_path,
            output_path=path_to_save)
        with self.transaction_manager as tm:
            source_img_id = self.image_repo.create_image(
                owner_user_id=user_id,
                file_path=str(source_path),
                image_format="PNG",
                channels_mask="RGB",
                file_size_bytes=result.size,
                sha256_hash=result.sha256,
                width_px=result.width,
                height_px=result.height
            )
            self.image_repo.create_image(
                owner_user_id=user_id,
                file_path=str(path_to_save),
                image_format="PNG",
                channels_mask="RGB",
                file_size_bytes=result.size,
                sha256_hash=result.sha256,
                width_px=result.width,
                height_px=result.height,
                is_stego=True,
                source_image_id=source_img_id
            )
            tm.commit()


class UnpackLSBImageToTextInteractor:

    def __init__(
            self,
            serializer: LSBSerializer,
            unpacker: LSBImageUnpacker,
            cipher_factory: CipherFactory,
            compressor_factory: CompressorFactory,
            password_hasher: PasswordHasher,
    ):
        self.serializer = serializer
        self.unpacker = unpacker
        self.cipher_factory = cipher_factory
        self.compressor_factory = compressor_factory
        self.password_hasher = password_hasher

    def execute(self, path_to_image: Path, password: str | None = None) -> str:
        raw_data = self.unpacker.unpack(path_to_image)
        image_data = self.serializer.deserialize(raw_data)
        payload = image_data.data

        if image_data.meta.encryption != Encryption.NONE:
            if password is None:
                raise ValueError("Password is required for decryption.")
            cipher = self.cipher_factory.get_cipher(image_data.meta.encryption)
            payload = cipher.decrypt(
                data=payload,
                key=self.password_hasher.hash(password),
            )
        if image_data.meta.compression != Compression.NONE:
            compressor = self.compressor_factory.get_compressor(image_data.meta.compression)
            payload = compressor.decompress(payload)

        return payload.decode("utf-8")
