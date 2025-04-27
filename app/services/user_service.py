from typing import List, Mapping
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import hash_password
from app.models.user import User, UserRole
from app.schemas.user import UserUpdate


class UserService:

    def __init__(self, db: Session):
        self.db = db

    async def get_all_users(self) -> List[User]:
        return self.db.query(User).all()

    async def create_admin(self, username: str, password: str) -> User:
        user = self.db.query(User).filter(User.username == username).first()
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
        user = self.db.query(User).filter(User.phone_number == phone_number).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
        return user

    async def get_or_create_by_phone(self, phone_number: str) -> Mapping[User, bool]:
        user = self.db.query(User).filter(User.phone_number == phone_number).first()
        created = False

        if not user:
            user = User(phone_number=phone_number)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            self.created = True
            
        return user, created

    async def get_user_by_id(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
        return user
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        user = await self.get_user_by_id(user_id)

        for key, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)
        return user
    
    async def delete_user(self, user_id: int) -> None:
        user = await self.get_user_by_id(user_id)
        self.db.delete(user)
        self.db.commit()
