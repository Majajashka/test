from dataclasses import dataclass
from typing import Optional

try:
    from .connection import db_cursor
    from .exceptions import RecordNotFoundError
except ImportError:
    from connection import db_cursor
    from exceptions import RecordNotFoundError


@dataclass
class Algorithm:
    id: int
    category: str
    code: str
    enum_value: Optional[int]
    version: str
    description: Optional[str]
    is_active: bool

    @staticmethod
    def from_row(row) -> "Algorithm":
        return Algorithm(
            id=row["id"],
            category=row["category"],
            code=row["code"],
            enum_value=row["enum_value"],
            version=row["version"],
            description=row["description"],
            is_active=bool(row["is_active"]),
        )


class AlgorithmRepository:
    def get_by_id(self, algo_id: int) -> Algorithm:
        with db_cursor() as cur:
            cur.execute("SELECT * FROM algorithms WHERE id = ?", (algo_id,))
            row = cur.fetchone()
            if row is None:
                raise RecordNotFoundError(f"algorithm id={algo_id} ვერ მოიძებნა")
            return Algorithm.from_row(row)

    def get_active_by_category_and_code(self, category: str, code: str) -> Algorithm:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT * FROM algorithms
                WHERE category = ? AND code = ? AND is_active = 1
                ORDER BY version DESC
                LIMIT 1
                """,
                (category, code),
            )
            row = cur.fetchone()
            if row is None:
                raise RecordNotFoundError(f"აქტიური ალგორითმი {category}/{code} ვერ მოიძებნა")
            return Algorithm.from_row(row)

    def list_active_by_category(self, category: str) -> list[Algorithm]:
        with db_cursor() as cur:
            cur.execute(
                "SELECT * FROM algorithms WHERE category = ? AND is_active = 1 ORDER BY code",
                (category,),
            )
            return [Algorithm.from_row(row) for row in cur.fetchall()]

    def register_new_algorithm(
        self, category: str, code: str, enum_value: Optional[int] = None,
        version: str = "1", description: str = ""
    ) -> int:
        with db_cursor(commit=True) as cur:
            cur.execute(
                """
                INSERT INTO algorithms (category, code, enum_value, version, description)
                VALUES (?, ?, ?, ?, ?)
                """,
                (category, code, enum_value, version, description),
            )
            return cur.lastrowid
