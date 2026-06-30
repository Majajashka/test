from pathlib import Path

import pytest

from app.core.compression import CompressorFactory
from app.core.crypto.cipher import CipherFactory
from app.core.crypto.hasher import SHA256PasswordHasher
from app.core.image.image import ChannelsMask, Compression, Encryption
from app.core.image.packers.lsb import LSBConfig, LSBImagePacker, LSBImageUnpacker
from app.core.image.reader import ImageReader, ImageWriter
from app.core.image.serializers import LSBSerializer
from app.core.usecases.pack_lsb import PackTextToLSBImageInteractor, UnpackLSBImageToTextInteractor

CARRIER_IMAGE = Path(__file__).parent / "test.png"
LSB_CONFIG = LSBConfig(red_bits=1, green_bits=1, blue_bits=1)


@pytest.fixture
def pack_interactor() -> PackTextToLSBImageInteractor:
    reader = ImageReader(mode=ChannelsMask.RGB)
    writer = ImageWriter(mode=ChannelsMask.RGB)
    return PackTextToLSBImageInteractor(
        serializer=LSBSerializer(),
        packer=LSBImagePacker(reader=reader, writer=writer, config=LSB_CONFIG),
        cipher_factory=CipherFactory(),
        compressor_factory=CompressorFactory(),
        password_hasher=SHA256PasswordHasher(),
    )


@pytest.fixture
def unpack_interactor() -> UnpackLSBImageToTextInteractor:
    reader = ImageReader(mode=ChannelsMask.RGB)
    return UnpackLSBImageToTextInteractor(
        serializer=LSBSerializer(),
        unpacker=LSBImageUnpacker(reader=reader),
        cipher_factory=CipherFactory(),
        compressor_factory=CompressorFactory(),
        password_hasher=SHA256PasswordHasher(),
    )


@pytest.mark.parametrize(
    "text, compression, encryption, password",
    [
        ("hello", Compression.NONE, Encryption.NONE, None),
        ("abc", Compression.GZIP, Encryption.XOR, "password"),
        ("test", Compression.GZIP, Encryption.ChaCha20, "password"),
        ("long text here", Compression.ZLIB, Encryption.XOR, "password"),
        ("long text here", Compression.ZLIB, Encryption.ChaCha20, "password"),
    ],
)
def test_pack_data(
        text: str,
        compression: Compression,
        encryption: Encryption,
        password: str,
        pack_interactor: PackTextToLSBImageInteractor,
        unpack_interactor: UnpackLSBImageToTextInteractor,
        tmp_path: Path,
) -> None:
    text = "Hello, world! This is a test message to encode into a carrier image. It should be able to decode back to the original text."
    path_to_save = tmp_path / "output_lsb.png"

    pack_interactor.execute(
        text=text,
        source_path=CARRIER_IMAGE,
        path_to_save=path_to_save,
        compression=compression,
        encryption=encryption,
        password=password,
    )

    unpacked_text = unpack_interactor.execute(path_to_image=path_to_save, password=password)

    assert text == unpacked_text


@pytest.mark.parametrize("text", ["a", "🔥", " " * 10])
def test_edge_texts(
        text: str,
        pack_interactor: PackTextToLSBImageInteractor,
        unpack_interactor: UnpackLSBImageToTextInteractor,
        tmp_path: Path,
) -> None:
    path = tmp_path / "out_lsb.png"

    pack_interactor.execute(
        text=text,
        source_path=CARRIER_IMAGE,
        path_to_save=path,
        compression=Compression.NONE,
        encryption=Encryption.NONE,
        password=None,
    )

    result = unpack_interactor.execute(path)

    assert result == text
