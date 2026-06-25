from dataclasses import dataclass
from pathlib import Path

from app.core.image.reader import ImageReader, ImageWriter, ImageMeta


@dataclass
class LSBConfig:
    red_bits: int = 1
    green_bits: int = 1
    blue_bits: int = 1
    alpha_bits: int = 0


class LSBImagePacker:

    def __init__(self, reader: ImageReader, writer: ImageWriter, config: LSBConfig):
        self.image_writer = writer
        self.image_reader = reader
        self.config = config

    def pack(self, data: bytes, output_path: Path, source_path: Path) -> None:
        source_img_meta = self.image_reader.read_meta(source_path)
        bits_capacity = self.get_capacity_bits(source_img_meta)
        bytes_capacity = bits_capacity // 8

        if len(data) > bytes_capacity:
            raise ValueError(f"Data is too large ({len(data)} bytes)")



        self.image_writer.write(data, width, height, output_path)
        print(f"[DEBUG] Successfully packed {len(data)} bytes to {output_path}")

    def get_capacity_bits(self, meta: ImageMeta) -> int:
        pixels = meta.width * meta.height

        per_pixel = (
                self.config.red_bits
                + self.config.green_bits
                + self.config.blue_bits
                + (self.config.alpha_bits if meta.mode == "RGBA" else 0)
        )

        return pixels * per_pixel

    def get_channels(self, mode: str) -> int:
        return self.image_writer.CHANNELS[mode]
