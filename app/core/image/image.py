from dataclasses import dataclass
from enum import Enum, IntEnum, IntFlag


class Compression(Enum):
    NONE = 0
    ZLIB = 1
    GZIP = 2


class Encryption(Enum):
    NONE = 0
    XOR = 1
    ChaCha20 = 2


class PackingAlgorithm(IntEnum):
    RGB = 1
    LSB = 2


class ChannelsMask(IntEnum):
    RGB = 1
    RGBA = 2


@dataclass
class LSBMetadata:
    channels_mask: ChannelsMask
    bits_r: int
    bits_g: int
    bits_b: int
    bits_a: int
    size: int
    compression: Compression
    encryption: Encryption


@dataclass
class LSBImageData:
    meta: LSBMetadata
    data: bytes


@dataclass
class PayloadMetadata:
    filename: str | None
    size: int
    compression: Compression
    encryption: Encryption


@dataclass
class ImageData:
    meta: PayloadMetadata
    data: bytes

    def length(self) -> int:
        return self.meta.size
