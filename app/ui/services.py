from pathlib import Path
from sqlite3 import Connection

from app.core.compression import CompressorFactory
from app.core.crypto.cipher import CipherFactory
from app.core.crypto.hasher import SHA256PasswordHasher
from app.core.image.image import ChannelsMask
from app.core.image.packers.lsb import LSBConfig, LSBImagePacker, LSBImageUnpacker
from app.core.image.packers.raw_rgb import RGBImagePacker, RGBImageUnpacker
from app.core.image.reader import ImageReader, ImageWriter
from app.core.image.serializers import LSBSerializer, TextToImageSerializator
from app.core.usecases.pack_data import PackTextToImageInteractor, UnpackImageToTextInteractor
from app.core.usecases.pack_lsb import PackTextToLSBImageInteractor, UnpackLSBImageToTextInteractor
from app.core.usecases.user import AuthenticateUserInteractor, CreateUserInteractor
from app.database.connection import DB_PATH, get_connection
from app.database.image_repository import ImageRepository
from app.database.migrate import run_migrations
from app.database.transaction_manager import TransactionManager
from app.database.user_repository import UserRepository

LSB_CONFIG = LSBConfig(red_bits=1, green_bits=1, blue_bits=1)


def ensure_database():
    if not DB_PATH.exists():
        run_migrations(with_seed_data=True, close_con=False)


def rgb_pack_interactor(conn: Connection | None = None) -> PackTextToImageInteractor:
    conn = conn or get_connection()
    return PackTextToImageInteractor(
        image_repo=ImageRepository(conn),
        transaction_manager=TransactionManager(conn),
        rgb_packer=RGBImagePacker(writer=ImageWriter()),
        serializer=TextToImageSerializator(),
        cipher_factory=CipherFactory(),
        compressor_factory=CompressorFactory(),
        password_hasher=SHA256PasswordHasher(),
    )


def rgb_unpack_interactor() -> UnpackImageToTextInteractor:
    return UnpackImageToTextInteractor(
        unpacker=RGBImageUnpacker(reader=ImageReader()),
        serializer=TextToImageSerializator(),
        cipher_factory=CipherFactory(),
        compressor_factory=CompressorFactory(),
        password_hasher=SHA256PasswordHasher(),
    )


def lsb_pack_interactor() -> PackTextToLSBImageInteractor:
    conn = get_connection()
    reader = ImageReader(mode=ChannelsMask.RGB)
    writer = ImageWriter(mode=ChannelsMask.RGB)
    return PackTextToLSBImageInteractor(
        image_repo=ImageRepository(conn),
        transaction_manager=TransactionManager(conn),
        serializer=LSBSerializer(),
        packer=LSBImagePacker(reader=reader, writer=writer, config=LSB_CONFIG),
        cipher_factory=CipherFactory(),
        compressor_factory=CompressorFactory(),
        password_hasher=SHA256PasswordHasher(),
    )


def lsb_unpack_interactor() -> UnpackLSBImageToTextInteractor:
    reader = ImageReader(mode=ChannelsMask.RGB)
    return UnpackLSBImageToTextInteractor(
        serializer=LSBSerializer(),
        unpacker=LSBImageUnpacker(reader=reader),
        cipher_factory=CipherFactory(),
        compressor_factory=CompressorFactory(),
        password_hasher=SHA256PasswordHasher(),
    )


def get_user_auth_interactor() -> AuthenticateUserInteractor:
    conn = get_connection()
    return AuthenticateUserInteractor(
        UserRepository(conn),
    )


def create_user_interactor() -> CreateUserInteractor:
    conn = get_connection()
    return CreateUserInteractor(
        UserRepository(conn),
        TransactionManager(conn),
    )
