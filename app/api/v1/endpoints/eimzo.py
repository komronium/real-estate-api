from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.eimzo import Base64Dto
from app.schemas.auth import Token
from app.services.esignature_service import ESignatureService

router = APIRouter(
    prefix='/api/v1/auth',
    tags=['Authentication']
)


@router.post(
    '/eimzo',
    response_model=Token,
    status_code=status.HTTP_200_OK,
    responses={
        400: {'description': 'Invalid credentials'},
        401: {'description': 'Authentication failed'},
        500: {'description': 'Internal Server Error'}
    }
)
async def login_with_eimzo(
    dto: Base64Dto,
    db: Session = Depends(get_db)
) -> Token:
    esignature_service = ESignatureService(db)
    return await esignature_service.authenticate(dto)
