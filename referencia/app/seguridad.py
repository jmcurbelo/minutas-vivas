"""Contraseñas y códigos de restablecimiento.

Argon2id es el algoritmo recomendado hoy (OWASP). Genera una SAL aleatoria por
contraseña y la guarda dentro del propio hash: $argon2id$v=19$m=...,t=...,p=...$<sal>$<hash>
"""
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

_hasher = PasswordHasher()  # parámetros por defecto de argon2-cffi (Argon2id)

LARGO_MINIMO = 10


def hashear(texto: str) -> str:
    return _hasher.hash(texto)


def verificar(hash_guardado: str, texto: str) -> bool:
    try:
        return _hasher.verify(hash_guardado, texto)
    except (VerificationError, InvalidHashError):
        return False


def generar_codigo() -> str:
    """Código de 6 dígitos con un generador criptográficamente seguro."""
    return f"{secrets.randbelow(1_000_000):06d}"


def validar_password(password: str) -> str | None:
    """Devuelve un mensaje de error o None si la contraseña es aceptable."""
    if len(password) < LARGO_MINIMO:
        return f"La contraseña debe tener al menos {LARGO_MINIMO} caracteres."
    return None
