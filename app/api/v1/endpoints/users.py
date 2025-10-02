from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.api.deps import get_db, get_admin_user, get_current_user
from app.schemas.user import UserAdminCreate, UserUpdate, UserOut
from app.services.user_service import UserService
from app.schemas.ad import AdOut

router = APIRouter(
    prefix='/api/v1/users',
    tags=['Users'],
)


@router.get(
    '/',
    response_model=List[UserOut],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_admin_user)],
    responses={
        401: {'description': 'Unauthorized'}
    }
)
async def list_users(db: Session = Depends(get_db)) -> List[UserOut]:
    user_service = UserService(db)
    return await user_service.get_all_users()


@router.post(
    '/',
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_admin_user)],
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
    user_id: UUID,
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    return user_service.get_user_by_id(user_id)


@router.patch(
    '/{user_id}',
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_admin_user)],
    responses={
        401: {'description': 'Unauthorized'},
        404: {'description': 'Not found'}
    }
)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
) -> User:
    user_service = UserService(db)
    return await user_service.update_user(user_id, user_data)


@router.delete(
    '/{user_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_admin_user)],
    responses={
        401: {'description': 'Unauthorized'},
        404: {'description': 'Not found'}
    }
)
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db)
) -> None:
    user_service = UserService(db)
    await user_service.delete_user(user_id)


@router.post('/me/favourites/{ad_id}', status_code=status.HTTP_201_CREATED)
async def add_favourite(
    ad_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = UserService(db)
    fav = service.add_favourite(current_user.id, ad_id)
    return {"id": fav.id, "ad_id": fav.ad_id, "created_at": fav.created_at}


@router.delete('/me/favourites/{ad_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_favourite(
    ad_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = UserService(db)
    service.remove_favourite(current_user.id, ad_id)
    return


@router.get('/me/favourites', response_model=List[AdOut])
async def list_my_favourites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = UserService(db)
    return service.list_favourites(current_user.id)
