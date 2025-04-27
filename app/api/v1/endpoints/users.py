from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.api.deps import get_db, get_admin_user
from app.schemas.user import UserAdminCreate, UserUpdate, UserOut
from app.services.user_service import UserService

router = APIRouter(
    prefix='/api/v1/users',
    tags=['Users'],
    dependencies=[Depends(get_admin_user)]
)


@router.get(
    '/',
    response_model=List[UserOut],
    status_code=status.HTTP_200_OK,
    responses={
        401: {'description': 'Unauthorized'}
    }
)
async def list_users(
        db: Session = Depends(get_db)
) -> List[UserOut]:
    user_service = UserService(db)
    return await user_service.get_all_users()


@router.post(
    '/',
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {'description': 'Invalid credentials'},
        401: {'description': 'Unauthorized'}
    }
)
async def create_admin(
    user: UserAdminCreate,
    db: Session = Depends(get_db)
) -> User:
    user_service = UserService(db)
    return await user_service.create_admin(user.username, user.password)


@router.get(
    '/{user_id}',
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    responses={
        401: {'description': 'Unauthorized'},
        404: {'description': 'Not found'}
    }
)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    return await user_service.get_user_by_id(user_id)


@router.patch(
    '/{user_id}',
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    responses={
        401: {'description': 'Unauthorized'},
        404: {'description': 'Not found'}
    }
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
) -> User:
    user_service = UserService(db)
    return await user_service.update_user(user_id, user_data)


@router.delete(
    '/{user_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {'description': 'Unauthorized'},
        404: {'description': 'Not found'}
    }
)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
) -> None:
    user_service = UserService(db)
    await user_service.delete_user(user_id)
