import sqlite3
from dataclasses import dataclass
from typing import Optional


@dataclass
class Operation:
    id: int
    user_id: int
    operation_type: str
    image_id: int
    payload_id: Optional[int]
    status: str
    error_message: Optional[str]
    duration_ms: Optional[int]
    created_at: str

    @staticmethod
    def from_row(row) -> "Operation":
        return Operation(
            id=row["id"],
            user_id=row["user_id"],
            operation_type=row["operation_type"],
            image_id=row["image_id"],
            payload_id=row["payload_id"],
            status=row["status"],
            error_message=row["error_message"],
            duration_ms=row["duration_ms"],
            created_at=row["created_at"],
        )


class OperationRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def log_operation(
        self,
        user_id: int,
        operation_type: str,
        image_id: int,
        status: str,
        payload_id: Optional[int] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
    ) -> int:
        cur = self.connection.cursor()
        cur.execute(
            """
            INSERT INTO operations (
                user_id, operation_type, image_id, payload_id,
                status, error_message, duration_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id, operation_type, image_id, payload_id,
                status, error_message, duration_ms,
            ),
        )
        return cur.lastrowid

    def list_by_user(self, user_id: int, limit: int = 50) -> list[Operation]:
        cur = self.connection.cursor()
        cur.execute(
            "SELECT * FROM operations WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        )
        return [Operation.from_row(row) for row in cur.fetchall()]

    def list_by_image(self, image_id: int) -> list[Operation]:
        cur = self.connection.cursor()
        cur.execute(
            "SELECT * FROM operations WHERE image_id = ? ORDER BY created_at DESC",
            (image_id,),
        )
        return [Operation.from_row(row) for row in cur.fetchall()]
