from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID

from app.core.security import hash_password
from app.models.user import User, UserRole
from app.schemas.user import UserUpdate


class UserService:

    def __init__(self, db: Session):
        self.db = db

    async def get_all_users(self) -> List[User]:
        """Get all users"""
        return self.db.query(User).all()

    def create_admin(self, username: str, password: str) -> User:
        """Create a new admin user"""
        user = self.get_by_username(username=username)
        if user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username already exists')

        user = User(
            username=username,
            password=hash_password(password),
            role=UserRole.ADMIN,
        )
            
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    async def get_by_phone(self, phone_number: str) -> User:
        """Get user by phone number"""
        user = self.db.query(User).filter(User.phone_number == phone_number).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
        return user
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()

    async def get_or_create_by_phone(self, phone_number: str) -> Tuple[User, bool]:
        """Get user by phone number or create if not exists"""
        user = self.db.query(User).filter(User.phone_number == phone_number).first()
        created = False

        if not user:
            user = User(phone_number=phone_number)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            created = True
            
        return user, created

    def get_user_by_id(self, user_id: str) -> User:
        """Get user by ID (UUID string)"""
        try:
            # Convert string to UUID if needed
            if isinstance(user_id, str):
                user_id = UUID(user_id)
            
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
            return user
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid user ID format')
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update user information"""
        user = self.get_user_by_id(user_id)

        for key, value in user_data.model_dump(exclude_unset=True).items():
            if key == "password":
                value = hash_password(value)
            setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: int) -> None:
        """Delete user"""
        user = self.get_user_by_id(user_id)
        self.db.delete(user)
        self.db.commit()
