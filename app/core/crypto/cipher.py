import os
from typing import Protocol

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from app.core.bytes_tool import ByteReader
from itertools import cycle

from app.core.exceptions import WrongPasswordError
from app.core.image.image import Encryption


class Cipher(Protocol):
    def encrypt(self, data: bytes, key: bytes) -> bytes:
        raise NotImplementedError

    def decrypt(self, data: bytes, key: bytes) -> bytes:
        raise NotImplementedError


class CipherFactory:
    @staticmethod
    def get_cipher(cipher: Encryption) -> Cipher:
        if cipher == Encryption.ChaCha20:
            return ChaCha20Cipher()
        elif cipher == Encryption.XOR:
            return XorCipher()
        else:
            raise ValueError(f"Unknown cipher: {cipher}")


class ChaCha20Cipher(Cipher):
    NONCE_SIZE = 12

    def encrypt(self, data: bytes, key: bytes) -> bytes:
        if len(key) != 32:
            raise ValueError("ChaCha20Poly1305 requires 32-byte key")

        nonce = os.urandom(self.NONCE_SIZE)

        cipher = ChaCha20Poly1305(key)
        ciphertext = cipher.encrypt(nonce, data, associated_data=None)

        return nonce + ciphertext

    def decrypt(self, data: bytes, key: bytes) -> bytes:
        if len(key) != 32:
            raise ValueError("ChaCha20Poly1305 requires 32-byte key")

        byte_data = ByteReader(data)

        nonce = byte_data.read(self.NONCE_SIZE)
        ciphertext = byte_data.read_all()

        cipher = ChaCha20Poly1305(key)

        try:
            data = cipher.decrypt(nonce, ciphertext, associated_data=None)
        except InvalidTag:
            raise WrongPasswordError("Wrong password")

        return data


class XorCipher(Cipher):
    SIGNATURE = b'XOR_SIGN'

    def encrypt(self, data: bytes, key: bytes) -> bytes:
        data_to_encrypt = self.SIGNATURE + data
        return bytes(b ^ key_b for b, key_b in zip(data_to_encrypt, cycle(key)))

    def decrypt(self, data: bytes, key: bytes) -> bytes:
        decrypted = bytes(b ^ key_b for b, key_b in zip(data, cycle(key)))

        if not decrypted.startswith(self.SIGNATURE):
            raise WrongPasswordError("Wrong password or invalid file format.")

        return decrypted[len(self.SIGNATURE):]
