import random
from math import ceil
from pathlib import Path

from app.core.image.reader import ImageWriter, ImageReader


class RGBImagePacker:

    def __init__(self, writer: ImageWriter, standard_sizes: list[tuple[int, int]] | None = None):
        self.standard_sizes = standard_sizes or [
            (16, 16),
            (32, 32),
            (64, 64),
            (128, 128),
            (256, 256),
            (512, 512),
            (1024, 1024),
            (1280, 720),
            (1920, 1080),
            (3840, 2160),
            (7680, 4320)
        ]
        self.image_writer = writer

    def pack(self, data: bytes, output_path: Path) -> None:
        pixels_needed = ceil(len(data) / 3)

        for width, height in self.standard_sizes:
            capacity = width * height
            print(f"[DEBUG] Checking size {width}x{height}, capacity={capacity}")

            if pixels_needed <= capacity:
                data = self.pad_to_size(data, width, height)
                self.image_writer.write_raw(data, width, height, output_path)
                print(f"[DEBUG] Successfully packed {len(data)} bytes to {output_path}")
                return

        raise ValueError(
            f"Data is too large ({len(data)} bytes)"
        )

    @staticmethod
    def pad_to_size(data: bytes, width: int, height: int) -> bytes:
        target_size = width * height * 3
        bytes_to_add = target_size - len(data)

        if bytes_to_add > 0:
            random_bytes = random.randbytes(bytes_to_add)
            data = data + random_bytes

        return data


class RGBImageUnpacker:

    def __init__(self, reader: ImageReader):
        self.image_reader = reader

    def unpack(self, image_path: Path) -> bytes:
        return self.image_reader.read_bytes(image_path)
