import hashlib
import hmac
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from app.database.exceptions import DuplicateUsernameError, InvalidCredentialsError, RecordNotFoundError

PBKDF2_ITERATIONS = 200_000


@dataclass
class User:
    id: int
    username: str
    password_hash: str
    password_algo: str
    password_salt: Optional[str]
    preferred_lang_code: str
    is_active: bool
    created_at: str
    last_login_at: Optional[str]

    @staticmethod
    def from_row(row) -> "User":
        return User(
            id=row["id"],
            username=row["username"],
            password_hash=row["password_hash"],
            password_algo=row["password_algo"],
            password_salt=row["password_salt"],
            preferred_lang_code=row["preferred_lang_code"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            last_login_at=row["last_login_at"],
        )


def _hash_password(password: str, salt: bytes) -> str:
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return derived.hex()


class UserRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def create_user(self, username: str, password: str, preferred_lang_code: str = "ka") -> int:
        salt = os.urandom(16)
        password_hash = _hash_password(password, salt)
        try:
            cur = self.connection.cursor()
            cur.execute(
                """
                INSERT INTO users (username, password_hash, password_algo, password_salt, preferred_lang_code)
                VALUES (?, ?, ?, ?, ?)
                """,
                (username, password_hash, "pbkdf2_sha256", salt.hex(), preferred_lang_code),
            )
            return cur.lastrowid
        except sqlite3.IntegrityError as exc:
            raise DuplicateUsernameError(f"username '{username}' უკვე დაკავებულია") from exc

    def get_by_username(self, username: str) -> User:
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        if row is None:
            raise RecordNotFoundError(f"მომხმარებელი '{username}' ვერ მოიძებნა")
        return User.from_row(row)

    def authenticate(self, username: str, password: str) -> User:
        try:
            user = self.get_by_username(username)
        except RecordNotFoundError:
            raise InvalidCredentialsError("username ან password არასწორია")

        if not user.is_active:
            raise InvalidCredentialsError("ანგარიში გათბილულია")

        salt = bytes.fromhex(user.password_salt)
        candidate_hash = _hash_password(password, salt)
        if not hmac.compare_digest(candidate_hash, user.password_hash):
            raise InvalidCredentialsError("username ან password არასწორია")

        return user

    def update_last_login(self, user_id: int) -> None:
        now = datetime.now(timezone.utc).isoformat(sep=" ", timespec="seconds")
        cur = self.connection.cursor()
        cur.execute("UPDATE users SET last_login_at = ? WHERE id = ?", (now, user_id))
