from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.ad import (
    GoldVerificationRequestCreate,
    GoldVerificationRequestOut,
    GoldVerificationRequestUpdate
)
from app.services.verification_service import VerificationService

router = APIRouter(prefix="/api/v1/verification", tags=["Gold Verification"])


@router.post(
    "/gold-request",
    response_model=GoldVerificationRequestOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Bad request - user not verified or request already exists"},
        404: {"description": "Ad not found or no permission"},
        500: {"description": "Internal server error"}
    }
)
async def request_gold_verification(
    request_data: GoldVerificationRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request gold verification for an ad
    
    Users must be verified with OneID before requesting gold verification.
    Only one pending request per ad is allowed.
    """
    verification_service = VerificationService(db)
    return verification_service.request_gold_verification(request_data, current_user)


@router.get(
    "/my-gold-requests",
    response_model=List[GoldVerificationRequestOut],
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def get_my_gold_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all gold verification requests made by the current user
    """
    verification_service = VerificationService(db)
    return verification_service.get_user_gold_requests(current_user)


@router.delete(
    "/gold-request/{request_id}",
    response_model=GoldVerificationRequestOut,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Bad request - request already processed"},
        401: {"description": "Unauthorized"},
        404: {"description": "Request not found or no permission"},
        500: {"description": "Internal server error"}
    }
)
async def cancel_gold_verification_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a pending gold verification request
    
    Only the user who made the request can cancel it.
    Only pending requests can be cancelled.
    """
    verification_service = VerificationService(db)
    return verification_service.cancel_gold_verification_request(request_id, current_user)
