from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from app.core.image.image import ChannelsMask


@dataclass
class ImageMeta:
    width: int
    height: int
    mode: ChannelsMask


class ImageReader:

    def __init__(
            self,
            mode: ChannelsMask = ChannelsMask.RGB,
            allowed_formats: list[str] | None = None,
    ):
        self._channels = 3  # currently only RGB is supported

        self.mode = mode
        self.allowed_formats = allowed_formats or ["PNG"]

    def read_bytes(self, image_path: str | Path) -> bytes:
        return self.read_pixels(image_path).tobytes()

    def read_pixels(self, image_path: str | Path) -> np.ndarray:
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"File {image_path} does not exist"
            )

        self._check_format(image_path)

        image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"Failed to read image: {image_path}")

        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    @staticmethod
    def read_meta(image_path: str | Path) -> ImageMeta:
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"File {image_path} does not exist"
            )

        image = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)
        if image is None:
            raise ValueError(f"Failed to read image: {image_path}")

        height, width, _ = image.shape  # height, width, channels
        return ImageMeta(
            width=width,
            height=height,
            mode=ChannelsMask.RGB,
        )
    @staticmethod
    def read_meta_from_pixels(pixels: np.ndarray) -> ImageMeta:
        height, width, _ = pixels.shape  # height, width, channels
        return ImageMeta(
            width=width,
            height=height,
            mode=ChannelsMask.RGB,
        )

    def _check_format(self, image_path: Path) -> None:
        suffix = image_path.suffix.lstrip(".").upper()
        if suffix not in self.allowed_formats:
            raise ValueError(
                f"Format {suffix or 'unknown'} is not allowed. "
                f"Allowed: {', '.join(self.allowed_formats)}"
            )


class ImageWriter:

    def __init__(self, mode: ChannelsMask = ChannelsMask.RGB):
        self.mode = mode
        self._channels = 3  # currently only RGB is supported

    def write_raw(self, data: bytes, width: int, height: int, path: Path) -> None:
        if len(data) != width * height * self._channels:
            raise ValueError("Data size does not match image dimensions")

        pixels = np.frombuffer(data, dtype=np.uint8).reshape(height, width, self._channels)
        self.write_pixels(pixels, width, height, path)

    def write_pixels(
            self, data: np.ndarray, width: int, height: int, path: Path
    ) -> None:
        pixels = np.asarray(data, dtype=np.uint8)

        if pixels.size != width * height * self._channels:
            raise ValueError("Data size does not match image dimensions")

        if pixels.ndim == 1:
            pixels = pixels.reshape(height, width, self._channels)
        elif pixels.shape != (height, width, self._channels):
            raise ValueError("Data size does not match image dimensions")

        bgr = cv2.cvtColor(pixels, cv2.COLOR_RGB2BGR)
        suffix = path.suffix.lower() or ".png"
        success, encoded = cv2.imencode(suffix, bgr)
        if not success:
            raise ValueError(f"Failed to write image: {path}")
        path.write_bytes(encoded.tobytes())
