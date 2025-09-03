from typing import Optional
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    verify_password
)
from app.models.user import User, UserRole
from app.schemas.auth import LoginAdminRequest, Token
from app.services.user_service import UserService


class AuthService:

    def __init__(self, db: Session):
        self.db = db

    def authenticate_admin(self, username: str, password: str) -> Optional[User]:
        """Authenticate admin user with username and password"""
        user = self.db.query(User).filter(User.username == username, User.role == UserRole.ADMIN).first()
        if not user or not verify_password(password, user.password):
            return None
        return user

    def login_admin(self, request: LoginAdminRequest) -> Token:
        """Login admin user and return access token"""
        user = self.authenticate_admin(request.username, request.password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')

        return self.generate_tokens(user)

    async def generate_tokens(self, user: User) -> Token:
        """Generate access and refresh tokens for user"""
        access_token = create_access_token({'sub': str(user.id)})
        refresh_token = create_refresh_token({'sub': str(user.id), 'type': 'refresh'})
        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    def refresh_token(self, refresh_token: str) -> Token:
        """Refresh access token using refresh token"""
        payload = decode_access_token(refresh_token)

        if not payload or payload.get('type') != 'refresh':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')
        
        user_service = UserService(self.db)
        user = user_service.get_user_by_id(payload['sub'])
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
        
        return self.generate_tokens(user)
