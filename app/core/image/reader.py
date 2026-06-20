import random
from itertools import batched

from math import ceil
from pathlib import Path

from PIL import Image


class RGBImageReader:

    def __init__(self, allowed_formats: list[str] = None):
        if allowed_formats is None:
            allowed_formats = []

        self.allowed_formats = allowed_formats

    def read(self, image_path: str | Path) -> bytes:
        """reads image and returns list of pixels in RGB format (tuple of 3 int8)"""
        if isinstance(image_path, str):
            image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"File {image_path} does not exist")

        image = Image.open(image_path, 'r', formats=['PNG'])

        if image.mode != 'RGB':
            image = image.convert('RGB')

        pixels = list(image.get_flattened_data())
        image_bytes = self._pixels_to_bytes(pixels)
        return image_bytes

    @staticmethod
    def _pixels_to_bytes(pixels: list[tuple[int, int, int]]) -> bytes:
        data = []

        for pixel in pixels:
            data.extend(pixel)

        return bytes(data)


class RGBImageWriter:

    def __init__(
            self,
            allowed_formats: list[str] = None,
            standard_sizes: list[tuple[int, int]] = None
    ):
        if allowed_formats is None:
            allowed_formats = []
        self.sizes = standard_sizes
        self.allowed_formats = allowed_formats

    def write(self, data: bytes, path: Path) -> None:
        pixels_needed = ceil(len(data) / 3)
        print(f"[INFO] Writing data: {len(data)} bytes, pixels needed: {pixels_needed}")

        ext = path.name.split('.')[-1]
        if ext not in self.allowed_formats:
            print(f"[ERROR] Invalid format: {ext}. Allowed: {self.allowed_formats}")
            raise ValueError(f"Invalid file format {ext}")

        for width, height in self.sizes:
            capacity = width * height
            print(f"[DEBUG] Checking size {width}x{height}, capacity={capacity}")

            if pixels_needed <= capacity:
                image = Image.new('RGB', (width, height))
                print(f"[DEBUG] Image created")

                data = self.pad_to_size(data, width, height)

                image.putdata(self._bytes_to_pixels(data))
                image.save(path)
                print(f"[INFO] Success: Saved to {path}")
                return
        else:
            print(f"[ERROR] Data too large for any standard size!")
            raise ValueError(f"Image is too large for any of the standard sizes:\n {self.sizes}")

    @staticmethod
    def pad_to_size(data: bytes, width: int, height: int) -> bytes:
        target_size = width * height * 3
        bytes_to_add = target_size - len(data)

        if bytes_to_add > 0:
            random_bytes = random.randbytes(bytes_to_add)
            data = data + random_bytes
            print(f"[DEBUG] Padded with {bytes_to_add} random bytes")

        return data

    @staticmethod
    def _bytes_to_pixels(data: bytes) -> tuple[tuple[int, int, int]]:
        print(f"[DEBUG] Converting {len(data)} bytes to pixel tuples...")
        return tuple(batched(data, 3, strict=True))
