from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_admin_user
from app.models.user import User
from app.schemas.ad import (
    GoldVerificationRequestOut,
    GoldVerificationRequestUpdate
)
from app.services.verification_service import VerificationService

router = APIRouter(prefix="/api/v1/admin/verification", tags=["Admin - Gold Verification"])


@router.get(
    "/pending-gold-requests",
    response_model=List[GoldVerificationRequestOut],
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Admin access required"},
        500: {"description": "Internal server error"}
    }
)
async def get_pending_gold_requests(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all pending gold verification requests
    
    Admin only endpoint to view all requests waiting for approval/rejection.
    """
    verification_service = VerificationService(db)
    return verification_service.get_pending_gold_requests()


@router.put(
    "/gold-request/{request_id}/process",
    response_model=GoldVerificationRequestOut,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Bad request - request already processed"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Admin access required"},
        404: {"description": "Request not found"},
        500: {"description": "Internal server error"}
    }
)
async def process_gold_verification_request(
    request_id: int,
    update_data: GoldVerificationRequestUpdate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Process a gold verification request (approve or reject)
    
    Admin only endpoint to approve or reject gold verification requests.
    When approved, the ad gets gold status and appears higher in listings.
    """
    verification_service = VerificationService(db)
    return verification_service.process_gold_verification_request(
        request_id, update_data, admin_user
    )


@router.get(
    "/all-gold-requests",
    response_model=List[GoldVerificationRequestOut],
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Admin access required"},
        500: {"description": "Internal server error"}
    }
)
async def get_all_gold_requests(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all gold verification requests (all statuses)
    
    Admin only endpoint to view all gold verification requests regardless of status.
    """
    verification_service = VerificationService(db)
    return verification_service.get_all_gold_requests()
