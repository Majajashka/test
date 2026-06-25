import random
from math import ceil
from pathlib import Path

from app.core.image.reader import ImageWriter


class RGBImagePacker:

    def __init__(self, writer: ImageWriter, standard_sizes: list[tuple[int, int]]):
        self.standard_sizes = standard_sizes
        self.image_writer = writer

    def pack(self, data: bytes, output_path: Path, source_path: Path | None = None) -> None:
        if source_path:
            raise ValueError("Source path is not supported for RGB packing algorithm")

        pixels_needed = ceil(len(data) / 3)

        for width, height in self.standard_sizes:
            capacity = width * height
            print(f"[DEBUG] Checking size {width}x{height}, capacity={capacity}")

            if pixels_needed <= capacity:
                data = self.pad_to_size(data, width, height)
                self.image_writer.write(data, width, height, output_path)
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
