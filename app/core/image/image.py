from dataclasses import dataclass
from enum import Enum


class Compression(Enum):
    NONE = 0
    ZLIB = 1
    GZIP = 2


class Encryption(Enum):
    NONE = 0
    XOR = 1
    ChaCha20 = 2


@dataclass
class PayloadMetadata:
    size: int
    filename: str | None
    compression: Compression
    encryption: Encryption


@dataclass
class ImageData:
    meta: PayloadMetadata
    data: bytes

    def length(self) -> int:
        return self.meta.size
