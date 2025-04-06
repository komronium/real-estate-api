from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.otp import OTPRequest


class UserService:

    @staticmethod
    async def get_all_users(db: Session) -> List[User]:
        return db.query(User).all()

    @staticmethod
    async def create_user(user_data: UserCreate, db: Session) -> User:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Email already exists'
            )

        hashed_password = hash_password(user_data.password)
        user = User(
            email=user_data.email,
            password=hashed_password,
            name=user_data.name
        )
            
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    async def get_by_phone(phone_number: str, db: Session) -> User:
        user = db.query(User).filter(User.phone_number == phone_number).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )
        return user

    @staticmethod
    async def get_or_create_by_phone(phone_number: str, db: Session) -> User:
        user = db.query(User).filter(User.phone_number == phone_number).first()
        created = False
        if not user:
            user = User(phone_number=phone_number)
            db.add(user)
            db.commit()
            db.refresh(user)
            created = True
        return user, created

    @staticmethod
    async def get_user_by_id(user_id: int, db: Session) -> User:
        return UserService._get_user_or_404(db, user_id)
    

    @staticmethod
    async def update_user(db: Session, user_id: int, user: UserUpdate) -> User:
        db_user = UserService._get_user_or_404(db, user_id)
        for key, value in user.model_dump().items():
            if value is not None:
                setattr(db_user, key, value)

        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def delete_user(db: Session, user_id: int) -> None:
        db_user = UserService._get_user_or_404(db, user_id)
        db.delete(db_user)
        db.commit()
