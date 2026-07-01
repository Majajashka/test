from pathlib import Path

import pytest

from app.core.compression import CompressorFactory
from app.core.crypto.cipher import CipherFactory
from app.core.crypto.hasher import SHA256PasswordHasher
from app.core.image.image import Compression, Encryption
from app.core.image.packers.raw_rgb import RGBImagePacker, RGBImageUnpacker
from app.core.image.reader import ImageWriter, ImageReader
from app.core.image.serializers import TextToImageSerializator
from app.core.usecases.pack_data import PackTextToImageInteractor, UnpackImageToTextInteractor
from app.database.connection import get_connection
from app.database.image_repository import ImageRepository
from app.database.transaction_manager import TransactionManager


@pytest.fixture
def pack_interactor() -> PackTextToImageInteractor:
    conn = get_connection()
    return PackTextToImageInteractor(
        image_repo=ImageRepository(conn),
        transaction_manager=TransactionManager(conn),
        rgb_packer=RGBImagePacker(
            writer=ImageWriter(),
        ),
        serializer=TextToImageSerializator(),
        cipher_factory=CipherFactory(),
        compressor_factory=CompressorFactory(),
        password_hasher=SHA256PasswordHasher()
    )


@pytest.fixture
def unpack_interactor() -> UnpackImageToTextInteractor:
    return UnpackImageToTextInteractor(
        unpacker=RGBImageUnpacker(
            reader=ImageReader()
        ),
        serializer=TextToImageSerializator(),
        cipher_factory=CipherFactory(),
        compressor_factory=CompressorFactory(),
        password_hasher=SHA256PasswordHasher()
    )


@pytest.mark.parametrize(
    "text, compression, encryption, password",
    [
        ("hello", Compression.NONE, Encryption.NONE, None),
        ("abc", Compression.GZIP, Encryption.XOR, "password"),
        ("test", Compression.GZIP, Encryption.ChaCha20, "password"),
        ("long text here", Compression.ZLIB, Encryption.XOR, "password"),
        ("long text here", Compression.ZLIB, Encryption.ChaCha20, "password"),
    ]
)
def test_pack_data(
        text: str,
        compression: Compression,
        encryption: Encryption,
        password: str,
        pack_interactor: PackTextToImageInteractor,
        unpack_interactor: UnpackImageToTextInteractor,
        tmp_path: Path
) -> None:
    text = "Hello, world! This is a test message to encode into a carrier image. It should be able to decode back to the original text."
    path_to_save = tmp_path / "output.png"

    pack_interactor.execute(
        user_id=1,
        text=text,
        path_to_save=tmp_path / "output.png",
        compression=compression,
        encryption=encryption,
        password=password
    )

    unpacked_text = unpack_interactor.execute(user_id=1,path_to_image=path_to_save,
                                              password=password)

    assert text == unpacked_text


@pytest.mark.parametrize("text", ["1", "a", "🔥", " " * 10])
def test_edge_texts(
        text,
        pack_interactor,
        unpack_interactor,
        tmp_path,
):
    path = tmp_path / "out.png"

    pack_interactor.execute(
        user_id=1,
        text=text,
        path_to_save=path,
        compression=Compression.NONE,
        encryption=Encryption.NONE,
        password=None,
    )

    result = unpack_interactor.execute(path_to_image=path)

    assert result == text
