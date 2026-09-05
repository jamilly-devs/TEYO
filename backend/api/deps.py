from datetime import datetime
from typing import Optional

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.models.session import UserSession
from db.models.user import User
from db.session import get_db

SESSION_COOKIE_NAME = "teyo_session"
SESSION_TTL_DAYS = 30

_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="not authenticated"
)


def get_current_user(
    teyo_session: Optional[str] = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    if teyo_session is None:
        raise _UNAUTHORIZED

    session = db.get(UserSession, teyo_session)
    if session is None or session.expires_at < datetime.utcnow():
        raise _UNAUTHORIZED

    user = db.get(User, session.user_id)
    if user is None:
        raise _UNAUTHORIZED

    return user
