from typing import Literal


class ByteReader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def read(self, n: int) -> bytes:
        result = self.data[self.pos: self.pos + n]
        self.pos += n
        return result

    def read_int(self, n: int, byteorder: Literal["little", "big"] = "big") -> int:
        return int.from_bytes(self.read(n), byteorder)

    def read_str(self, n: int, encoding: str = "utf-8") -> str:
        return self.read(n).decode(encoding)

    def read_all(self) -> bytes:
        result = self.data[self.pos:]
        self.pos = len(self.data)
        return result

    def reset(self):
        self.pos = 0


class ByteWriter:
    def __init__(self):
        self._buf = bytearray()

    def write_bytes(self, data: bytes):
        self._buf.extend(data)

    def write_int(self, value: int, size: int, byteorder: Literal["little", "big"] = "big"):
        self._buf.extend(value.to_bytes(size, byteorder))

    def write_str(self, value: str, encoding: str = "utf-8"):
        self._buf.extend(value.encode(encoding))

    def build(self) -> bytes:
        return bytes(self._buf)

    def length(self) -> int:
        return len(self._buf)
