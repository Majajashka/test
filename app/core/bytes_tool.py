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


class BitReader:
    def __init__(self, data: bytes):
        self.data = data
        self.byte_pos = 0
        self.bit_pos = 0

    def _ensure(self):
        if self.byte_pos >= len(self.data):
            raise EOFError("No more data")

    def read_bit(self) -> int:
        self._ensure()

        byte = self.data[self.byte_pos]
        bit = (byte >> self.bit_pos) & 1

        self.bit_pos += 1
        if self.bit_pos == 8:
            self.bit_pos = 0
            self.byte_pos += 1

        return bit

    def read_bits(self, n: int) -> int:
        value = 0

        for i in range(n):
            value |= (self.read_bit() << i)

        return value

    def align(self):
        if self.bit_pos != 0:
            self.bit_pos = 0
            self.byte_pos += 1

    def skip_bits(self, n: int):
        if n <= 0:
            return

        total_bits = self.byte_pos * 8 + self.bit_pos + n
        if total_bits > len(self.data) * 8:
            raise EOFError("No more data")

        self.byte_pos = total_bits // 8
        self.bit_pos = total_bits % 8

    def remaining_bits(self) -> int:
        return (len(self.data) * 8) - (self.byte_pos * 8 + self.bit_pos)


class BitBuffer:
    def __init__(self):
        self._value = 0
        self._count = 0

    def push(self, value: int, bits: int):
        self._value |= value << self._count
        self._count += bits

    def has_byte(self) -> bool:
        return self._count >= 8

    def pop_byte(self) -> int:
        if self._count < 8:
            raise ValueError("Not enough bits")

        result = self._value & 0xFF
        self._value >>= 8
        self._count -= 8
        return result


def set_low_bits(byte: int, amount: int, value: int) -> int:
    mask = (1 << amount) - 1
    return (byte & ~mask) | (value & mask)


def read_low_bits(byte: int, amount: int) -> int:
    return byte & ((1 << amount) - 1)
