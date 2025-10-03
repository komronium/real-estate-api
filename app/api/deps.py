from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.user import User, UserRole

oauth2_scheme = HTTPBearer()
oauth2_scheme_optional = HTTPBearer(auto_error=False)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials'
    )

    payload = decode_access_token(token.credentials)
    if not payload:
        raise credentials_exception

    user_id = payload.get('sub')
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_exception

    return user


async def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access forbidden',
        )
    return current_user


async def get_current_user_optional(
        db: Session = Depends(get_db),
        token: HTTPAuthorizationCredentials | None = Depends(oauth2_scheme_optional)
) -> User | None:
    """Return current user if Authorization provided and valid; otherwise None."""
    if not token:
        return None

    payload = decode_access_token(token.credentials)
    if not payload:
        return None

    user_id = payload.get('sub')
    user = db.query(User).filter(User.id == user_id).first()
    return user
