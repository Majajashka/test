import random
from dataclasses import dataclass
from itertools import batched

from math import ceil
from pathlib import Path

from PIL import Image

from app.core.image.image import ChannelsMask


@dataclass
class ImageMeta:
    width: int
    height: int
    mode: ChannelsMask


class ImageReader:
    CHANNELS = {
        "RGB": 3,
        "RGBA": 4,
    }

    def __init__(
            self,
            mode: str = "RGB",
            allowed_formats: list[str] | None = None,
    ):
        try:
            self.channels = self.CHANNELS[mode]
        except KeyError:
            raise ValueError(f"Unsupported mode: {mode}")

        self.mode = mode
        self.allowed_formats = allowed_formats or ["PNG"]

    def read_bytes(self, image_path: str | Path) -> bytes:
        pixels = self.read_pixels(image_path)
        return self._pixels_to_bytes(pixels)

    def read_pixels(self, image_path: str | Path) -> list[tuple[int, ...], ...]:
        if isinstance(image_path, str):
            image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"File {image_path} does not exist"
            )

        with Image.open(
                image_path,
                formats=self.allowed_formats,
        ) as image:
            if image.mode != self.mode:
                image = image.convert(self.mode)

            return image.get_flattened_data()

    def read_meta(self, image_path: str | Path) -> ImageMeta:
        with Image.open(image_path) as image:
            return ImageMeta(
                width=image.width,
                height=image.height,
                mode=ChannelsMask(image.mode),
            )

    @staticmethod
    def _pixels_to_bytes(pixels: list[tuple[int, ...], ...]) -> bytes:
        data = []

        for pixel in pixels:
            data.extend(pixel)

        return bytes(data)


class ImageWriter:
    CHANNELS = {
        "RGB": 3,
        "RGBA": 4,
    }

    def __init__(self, mode: str = "RGB"):
        try:
            self.mode = mode
            self._channels = self.CHANNELS[mode]
        except KeyError:
            raise ValueError(f"Unsupported mode: {mode}")

    def write(self, data: bytes, width: int, height: int, path: Path) -> None:
        if len(data) != width * height * self._channels:
            raise ValueError("Data size does not match image dimensions")
        image = Image.new(self.mode, (width, height))
        image.putdata(tuple(batched(data, self._channels, strict=True)))
        image.save(path)

    @property
    def channels(self) -> int:
        return self._channels

    def _bytes_to_pixels(self, data: bytes) -> tuple[tuple[int, ...]]:
        return tuple(batched(data, self._channels, strict=True))
