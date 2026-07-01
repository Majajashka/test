import sqlite3
from dataclasses import dataclass
from typing import Optional

from app.database.exceptions import RecordNotFoundError


@dataclass
class Image:
    id: int
    owner_user_id: int
    source_image_id: Optional[int]
    file_path: str
    original_name: Optional[str]
    image_format: str
    channels_mask: Optional[str]
    width_px: Optional[int]
    height_px: Optional[int]
    file_size_bytes: int
    sha256_hash: str
    is_stego: bool
    created_at: str

    @staticmethod
    def from_row(row) -> "Image":
        return Image(
            id=row["id"],
            owner_user_id=row["owner_user_id"],
            source_image_id=row["source_image_id"],
            file_path=row["file_path"],
            original_name=row["original_name"],
            image_format=row["image_format"],
            channels_mask=row["channels_mask"],
            width_px=row["width_px"],
            height_px=row["height_px"],
            file_size_bytes=row["file_size_bytes"],
            sha256_hash=row["sha256_hash"],
            is_stego=bool(row["is_stego"]),
            created_at=row["created_at"],
        )


class ImageRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def create_image(
        self,
        owner_user_id: int,
        file_path: str,
        image_format: str,
        file_size_bytes: int,
        sha256_hash: str,
        original_name: Optional[str] = None,
        channels_mask: Optional[str] = None,
        width_px: Optional[int] = None,
        height_px: Optional[int] = None,
        is_stego: bool = False,
        source_image_id: Optional[int] = None,
    ) -> int:
        cur = self.connection.cursor()
        cur.execute(
            """
            INSERT INTO images (
                owner_user_id, source_image_id, file_path, original_name,
                image_format, channels_mask, width_px, height_px,
                file_size_bytes, sha256_hash, is_stego
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                owner_user_id, source_image_id, file_path, original_name,
                image_format, channels_mask, width_px, height_px,
                file_size_bytes, sha256_hash, int(is_stego),
            ),
        )
        return cur.lastrowid

    def get_by_id(self, image_id: int) -> Image:
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM images WHERE id = ?", (image_id,))
        row = cur.fetchone()
        if row is None:
            raise RecordNotFoundError(f"image id={image_id} ვერ მოიძებნა")
        return Image.from_row(row)

    def list_by_owner(self, owner_user_id: int) -> list[Image]:
        cur = self.connection.cursor()
        cur.execute(
            "SELECT * FROM images WHERE owner_user_id = ? ORDER BY created_at DESC",
            (owner_user_id,),
        )
        return [Image.from_row(row) for row in cur.fetchall()]
