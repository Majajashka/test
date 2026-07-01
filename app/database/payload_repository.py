import sqlite3
from dataclasses import dataclass
from typing import Optional

from app.database.exceptions import RecordNotFoundError


@dataclass
class Payload:
    id: int
    image_id: int
    payload_type: str
    original_filename: Optional[str]
    mime_type: Optional[str]
    original_size_bytes: int
    embedded_size_bytes: int
    packing_algorithm: str
    compression_code: str
    encryption_code: str
    lsb_channels_mask: Optional[str]
    lsb_bits_r: Optional[int]
    lsb_bits_g: Optional[int]
    lsb_bits_b: Optional[int]
    lsb_bits_a: Optional[int]
    checksum_sha256: str
    created_at: str

    @staticmethod
    def from_row(row) -> "Payload":
        return Payload(
            id=row["id"],
            image_id=row["image_id"],
            payload_type=row["payload_type"],
            original_filename=row["original_filename"],
            mime_type=row["mime_type"],
            original_size_bytes=row["original_size_bytes"],
            embedded_size_bytes=row["embedded_size_bytes"],
            packing_algorithm=row["packing_algorithm"],
            compression_code=row["compression_code"],
            encryption_code=row["encryption_code"],
            lsb_channels_mask=row["lsb_channels_mask"],
            lsb_bits_r=row["lsb_bits_r"],
            lsb_bits_g=row["lsb_bits_g"],
            lsb_bits_b=row["lsb_bits_b"],
            lsb_bits_a=row["lsb_bits_a"],
            checksum_sha256=row["checksum_sha256"],
            created_at=row["created_at"],
        )


class PayloadRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def create_payload(
        self,
        image_id: int,
        payload_type: str,
        original_size_bytes: int,
        embedded_size_bytes: int,
        packing_algorithm: str,
        compression_code: str,
        encryption_code: str,
        checksum_sha256: str,
        original_filename: Optional[str] = None,
        mime_type: Optional[str] = None,
        lsb_channels_mask: Optional[str] = None,
        lsb_bits_r: Optional[int] = None,
        lsb_bits_g: Optional[int] = None,
        lsb_bits_b: Optional[int] = None,
        lsb_bits_a: Optional[int] = None,
    ) -> int:
        cur = self.connection.cursor()
        cur.execute(
            """
            INSERT INTO payloads (
                image_id, payload_type, original_filename, mime_type,
                original_size_bytes, embedded_size_bytes, packing_algorithm,
                compression_code, encryption_code,
                lsb_channels_mask, lsb_bits_r, lsb_bits_g, lsb_bits_b, lsb_bits_a,
                checksum_sha256
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                image_id, payload_type, original_filename, mime_type,
                original_size_bytes, embedded_size_bytes, packing_algorithm,
                compression_code, encryption_code,
                lsb_channels_mask, lsb_bits_r, lsb_bits_g, lsb_bits_b, lsb_bits_a,
                checksum_sha256,
            ),
        )
        return cur.lastrowid

    def get_by_image_id(self, image_id: int) -> Payload:
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM payloads WHERE image_id = ?", (image_id,))
        row = cur.fetchone()
        if row is None:
            raise RecordNotFoundError(f"image id={image_id}-ისთვის payload ვერ მოიძებნა")
        return Payload.from_row(row)
