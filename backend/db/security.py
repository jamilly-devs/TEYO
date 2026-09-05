"""Password hashing and session token generation.

Technical implementation detail (not a product decision): PBKDF2-HMAC-SHA256
via the standard library, with a random per-user salt. No extra dependency
required. Password strength policy (minimum length, complexity) is not
enforced here — `V1_SCOPE.md` marks "regras de segurança/privacidade" as
still A DEFINIR.
"""

import hashlib
import secrets

_ALGORITHM = "sha256"
_ITERATIONS = 100_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        _ALGORITHM, password.encode("utf-8"), salt.encode("utf-8"), _ITERATIONS
    )
    return f"{salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        salt, hex_digest = password_hash.split("$", 1)
    except ValueError:
        return False
    digest = hashlib.pbkdf2_hmac(
        _ALGORITHM, password.encode("utf-8"), salt.encode("utf-8"), _ITERATIONS
    )
    return secrets.compare_digest(digest.hex(), hex_digest)


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)
