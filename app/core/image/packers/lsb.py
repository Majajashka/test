from dataclasses import dataclass
from itertools import cycle
from math import ceil
from pathlib import Path

from app.core.bytes_tool import BitReader, set_low_bits, BitBuffer
from app.core.image.formats.lsb import LSBFormat
from app.core.image.image import LSBMetadata
from app.core.image.reader import ImageReader, ImageWriter, ImageMeta, WriteResult
from app.core.image.serializers import LSBSerializer


@dataclass
class LSBConfig:
    red_bits: int = 1
    green_bits: int = 1
    blue_bits: int = 1



class LSBImagePacker:

    def __init__(self, reader: ImageReader, writer: ImageWriter, config: LSBConfig):
        self.image_writer = writer
        self.image_reader = reader
        self.config = config

    def pack(
            self,
            data: bytes,
            source_image_path: Path,
            output_path: Path
    ) -> WriteResult:
        source_image_pixels = self.image_reader.read_pixels(source_image_path)
        source_image_meta = self.image_reader.read_meta_from_pixels(source_image_pixels)
        flat_pixels = source_image_pixels.reshape(-1, 3)
        total_pixels = len(flat_pixels)

        bits_capacity = self.get_capacity_bits(source_image_meta)
        bytes_capacity = bits_capacity // 8

        if len(data) > bytes_capacity:
            raise ValueError(f"Data is too large ({len(data)} bytes)")

        bit_reader = BitReader(data)

        bootstrap_bits_per_pixel = (
                LSBFormat.BOOTSTRAP_RED_BITS  # 1
                + LSBFormat.BOOTSTRAP_GREEN_BITS  # 1
                + LSBFormat.BOOTSTRAP_BLUE_BITS  # 1
        )
        header_bits = LSBFormat.HEADER_SIZE * 8
        header_pixels_count = ceil(header_bits / bootstrap_bits_per_pixel)
        bootstrap_config = self._bootstrap_config()
        header_limit = min(header_pixels_count, total_pixels)

        for i in range(header_limit):
            flat_pixels[i] = self.write_in_rgb_pixel(
                tuple(flat_pixels[i]), bit_reader, bootstrap_config
            )

        for i in range(header_limit, total_pixels):
            if bit_reader.remaining_bits() == 0:
                break
            flat_pixels[i] = self.write_in_rgb_pixel(tuple(flat_pixels[i]), bit_reader)

        result = self.image_writer.write_pixels(
            data=source_image_pixels,
            width=source_image_meta.width,
            height=source_image_meta.height,
            path=output_path
        )
        print(f"[DEBUG] Successfully packed {len(data)} bytes to {output_path}")
        return result

    @staticmethod
    def _bootstrap_config() -> LSBConfig:
        return LSBConfig(
            red_bits=LSBFormat.BOOTSTRAP_RED_BITS,
            green_bits=LSBFormat.BOOTSTRAP_GREEN_BITS,
            blue_bits=LSBFormat.BOOTSTRAP_BLUE_BITS,
        )

    def write_in_rgb_pixel(
            self,
            pixel: tuple[int, int, int],
            bit_reader: BitReader,
            config: LSBConfig | None = None
    ) -> tuple[int, int, int]:
        r, g, b = pixel
        r, g, b = int(r), int(g), int(b)

        config = config or self.config
        remaining = bit_reader.remaining_bits()

        if config.red_bits > 0 and remaining > 0:
            n = min(config.red_bits, remaining)
            r_bits = bit_reader.read_bits(n)
            r = set_low_bits(r, n, r_bits)
            remaining -= n

        if config.green_bits > 0 and remaining > 0:
            n = min(config.green_bits, remaining)
            g_bits = bit_reader.read_bits(n)
            g = set_low_bits(g, n, g_bits)
            remaining -= n

        if config.blue_bits > 0 and remaining > 0:
            n = min(config.blue_bits, remaining)
            b_bits = bit_reader.read_bits(n)
            b = set_low_bits(b, n, b_bits)

        return r, g, b

    def get_capacity_bits(self, meta: ImageMeta) -> int:
        """Returns the capacity of the image in bits"""
        total_pixels = meta.width * meta.height
        bootstrap_bits_per_pixel = (
                LSBFormat.BOOTSTRAP_RED_BITS
                + LSBFormat.BOOTSTRAP_GREEN_BITS
                + LSBFormat.BOOTSTRAP_BLUE_BITS
        )
        payload_bits_per_pixel = (
                self.config.red_bits
                + self.config.green_bits
                + self.config.blue_bits
        )
        header_pixels = ceil(LSBFormat.HEADER_SIZE * 8 / bootstrap_bits_per_pixel)
        payload_pixels = max(0, total_pixels - header_pixels)
        return LSBFormat.HEADER_SIZE * 8 + payload_pixels * payload_bits_per_pixel


class LSBReader:

    def __init__(self, data: bytes, config: LSBConfig):
        self.bit_reader = BitReader(data)
        self._channel_bits = cycle([config.red_bits, config.green_bits, config.blue_bits])
        self._channel_index = 0
        self._buffer = BitBuffer()

    def _next_channel_bits(self) -> int:
        return next(self._channel_bits)

    def read_bytes(self, count: int) -> bytes:
        out = bytearray()

        while len(out) < count:

            while not self._buffer.has_byte():
                bits = self._next_channel_bits()

                if bits == 0:
                    self.bit_reader.skip_bits(8)
                    continue

                value = self.bit_reader.read_bits(bits)
                self.bit_reader.skip_bits(8 - bits)

                self._buffer.push(value, bits)

            while self._buffer.has_byte() and len(out) < count:
                out.append(self._buffer.pop_byte())

        return bytes(out)

    def change_config(self, config: LSBConfig):
        self._channel_bits = cycle([config.red_bits, config.green_bits, config.blue_bits])


class LSBImageUnpacker:

    def __init__(self, reader: ImageReader):
        self.image_reader = reader

    def unpack(self, image_path: Path) -> bytes:
        raw_data = self.image_reader.read_bytes(image_path)
        lsb_reader = LSBReader(
            raw_data,
            LSBConfig(
                red_bits=LSBFormat.BOOTSTRAP_RED_BITS,
                green_bits=LSBFormat.BOOTSTRAP_GREEN_BITS,
                blue_bits=LSBFormat.BOOTSTRAP_BLUE_BITS,
            )
        )
        raw_metadata = lsb_reader.read_bytes(LSBFormat.HEADER_SIZE)
        metadata = LSBSerializer.deserialize_meta(raw_metadata)
        lsb_reader.change_config(LSBConfig(metadata.bits_r, metadata.bits_g, metadata.bits_b))
        payload = lsb_reader.read_bytes(metadata.size)
        return raw_metadata + payload

    @staticmethod
    def read_bootstrap(lsb_reader: LSBReader) -> LSBMetadata:
        raw_metadata = lsb_reader.read_bytes(LSBFormat.HEADER_SIZE)
        return LSBSerializer.deserialize_meta(raw_metadata)
