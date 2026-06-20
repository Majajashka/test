from typing import Protocol
from zlib import compress as zlib_compress, decompress as zlib_decompress
from gzip import compress as gzip_compress, decompress as gzip_decompress

from app.core.image.image import Compression


class Compressor(Protocol):

    def compress(self, data: bytes, level: int | None = None) -> bytes:
        raise NotImplementedError

    def decompress(self, data: bytes) -> bytes:
        raise NotImplementedError


class CompressorFactory:

    @staticmethod
    def get_compressor(compression: Compression) -> Compressor:
        if compression == Compression.ZLIB:
            return ZlibCompressor()
        elif compression == Compression.GZIP:
            return GzipCompressor()
        else:
            raise NotImplementedError


class ZlibCompressor(Compressor):

    def compress(self, data: bytes, level: int | None = None) -> bytes:
        if level is None:
            level = -1
        return zlib_compress(data, level)

    def decompress(self, data: bytes) -> bytes:
        return zlib_decompress(data)


class GzipCompressor(Compressor):

    def compress(self, data: bytes, level: int | None = None) -> bytes:
        if level is None:
            level = -1
        return gzip_compress(data, level)

    def decompress(self, data: bytes) -> bytes:
        return gzip_decompress(data)
