"""
Шифрование секретов для vault.secrets.

AES-256-GCM. Формат ciphertext:

    nonce (12 байт) || ciphertext+tag (переменная длина)

AAD (associated data) привязан к контексту записи:
    b"<project>:<key>:<key_version>"

Это значит, что ciphertext, зашифрованный для одной пары
(project, key, version), нельзя переложить в другую запись —
при расшифровке AAD не совпадёт и GCM вернёт ошибку.

API:
    encrypt(master_key: bytes, plaintext: bytes, aad: bytes) -> bytes
    decrypt(master_key: bytes, blob: bytes,     aad: bytes) -> bytes
    make_aad(project, key, key_version) -> bytes
"""

from __future__ import annotations

import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE_LEN = 12
KEY_LEN = 32  # AES-256


def make_aad(project: str, key: str, key_version: int) -> bytes:
    return f"{project}:{key}:{key_version}".encode("utf-8")


def encrypt(master_key: bytes, plaintext: bytes, aad: bytes) -> bytes:
    if len(master_key) != KEY_LEN:
        raise ValueError(f"master_key must be {KEY_LEN} bytes, got {len(master_key)}")
    nonce = os.urandom(NONCE_LEN)
    ct = AESGCM(master_key).encrypt(nonce, plaintext, aad)
    return nonce + ct


def decrypt(master_key: bytes, blob: bytes, aad: bytes) -> bytes:
    if len(master_key) != KEY_LEN:
        raise ValueError(f"master_key must be {KEY_LEN} bytes, got {len(master_key)}")
    if len(blob) < NONCE_LEN + 16:  # nonce + минимальный GCM tag
        raise ValueError("ciphertext too short")
    nonce, ct = blob[:NONCE_LEN], blob[NONCE_LEN:]
    return AESGCM(master_key).decrypt(nonce, ct, aad)