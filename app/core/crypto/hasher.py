import hashlib
from typing import Protocol


class PasswordHasher(Protocol):
    def hash(self, password: str) -> bytes:
        raise NotImplementedError


class SHA256PasswordHasher(PasswordHasher):
    def hash(self, password: str) -> bytes:
        return hashlib.sha256(password.encode("utf-8")).digest()
