import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.services.one_id_service import OneIDService
from app.schemas.one_id import (
    OneIDCodeRequest,
    UserWithOneIDResponse,
    OneIDInfoResponse
)
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["One ID Verification"])


@router.post("/one_id", response_model=UserWithOneIDResponse)
async def verify_with_one_id(
    request: OneIDCodeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify current user with One ID authorization code
    
    Only authenticated users can verify their identity with One ID.
    Returns updated user with One ID information.
    """
    try:
        one_id_service = OneIDService(db)
        
        # Exchange code for token
        token_response = await one_id_service.exchange_code_for_token(request.code)
        
        # Get user information
        user_info = await one_id_service.get_user_info(token_response.access_token)
        
        # Update current user with One ID information
        updated_user = one_id_service.update_current_user_with_one_id(current_user, user_info)
        
        # Check if the returned user is different from current user
        if updated_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This One ID is already linked to another user account"
            )
        
        # Convert to response format with One ID info
        one_id_info_response = None
        if updated_user.one_id_info:
            one_id_info_response = OneIDInfoResponse(
                id=updated_user.one_id_info.id,
                pin=updated_user.one_id_info.pin,
                one_id_user_id=updated_user.one_id_info.one_id_user_id,
                one_id_session_id=updated_user.one_id_info.one_id_session_id,
                full_name=updated_user.one_id_info.full_name,
                first_name=updated_user.one_id_info.first_name,
                last_name=updated_user.one_id_info.last_name,
                middle_name=updated_user.one_id_info.middle_name,
                passport_number=updated_user.one_id_info.passport_number,
                birth_date=updated_user.one_id_info.birth_date,
                user_type=updated_user.one_id_info.user_type,
                is_verified=updated_user.one_id_info.is_verified,
                validation_method=updated_user.one_id_info.validation_method,
                auth_method=updated_user.one_id_info.auth_method,
                pkcs_legal_tin=updated_user.one_id_info.pkcs_legal_tin,
                created_at=updated_user.one_id_info.created_at,
                updated_at=updated_user.one_id_info.updated_at
            )
        
        return UserWithOneIDResponse(
            id=updated_user.id,
            name=updated_user.name,
            username=updated_user.username,
            email=updated_user.email,
            phone_number=updated_user.phone_number,
            is_active=updated_user.is_active,
            is_verified=updated_user.is_verified,
            role=updated_user.role,
            one_id_info=one_id_info_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in One ID verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during One ID verification"
        )

