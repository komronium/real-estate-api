from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.auth import LoginAdminRequest, Token, RefreshTokenRequest

from app.services.auth_service import AuthService

router = APIRouter(
    prefix='/api/v1/auth',
    tags=['Authentication']
)


@router.post(
    '/login-admin',
    response_model=Token,
    status_code=status.HTTP_200_OK,
    responses={
        400: {'description': 'Invalid credentials'},
        401: {'description': 'Authentication failed'},
        500: {'description': 'Internal Server Error'}
    }
)
async def login_admin(
    request: LoginAdminRequest,
    db: Session = Depends(get_db)
) -> Token:
    auth_service = AuthService(db)
    return await auth_service.login_admin(request)


@router.post(
    '/refresh',
    response_model=Token,
    status_code=status.HTTP_200_OK,
    responses={
        400: {'description': 'Invalid credentials'},
        401: {'description': 'Authentication failed'},
        500: {'description': 'Internal Server Error'}
    }
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> Token:
    auth_service = AuthService(db)
    return await auth_service.refresh_token(request.refresh_token)
