"""Minimal development seed for FASE 1.

Creates exactly one placeholder user so there is something to develop and
test against locally after running migrations. Idempotent: safe to run more
than once. Assumes `alembic upgrade head` has already created the schema.

The password hashing below is a local-development placeholder only — it is
not a production authentication decision. The definitive hashing scheme
belongs to whatever registration/login tool is built later; nothing here
should be read as pre-deciding that.
"""

import hashlib
import os
import secrets
from typing import Optional

from db.models.user import User
from db.session import SessionLocal

DEFAULT_EMAIL = "dev@teyo.local"
DEFAULT_PASSWORD = "devpassword123"


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    )
    return f"{salt}${digest.hex()}"


def seed_dev_user(email: Optional[str] = None, password: Optional[str] = None) -> None:
    email = email or os.environ.get("SEED_USER_EMAIL", DEFAULT_EMAIL)
    password = password or os.environ.get("SEED_USER_PASSWORD", DEFAULT_PASSWORD)

    with SessionLocal() as session:
        existing = session.query(User).filter_by(email=email).one_or_none()
        if existing is not None:
            print(f"[seed] dev user already exists: {email}")
            return

        user = User(email=email, password_hash=_hash_password(password))
        session.add(user)
        session.commit()
        print(f"[seed] dev user created: {email} / password: {password}")


def main() -> None:
    seed_dev_user()


if __name__ == "__main__":
    main()
