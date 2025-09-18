from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.ad import Ad, GoldVerificationRequest, GoldVerificationStatus
from app.models.user import User
from app.schemas.ad import GoldVerificationRequestCreate, GoldVerificationRequestUpdate


class VerificationService:
    """Service for handling ad verification logic"""

    def __init__(self, db: Session):
        self.db = db

    def request_gold_verification(
        self, 
        request_data: GoldVerificationRequestCreate, 
        user: User
    ) -> GoldVerificationRequest:
        """
        Create a gold verification request for an ad
        """
        # Check if ad exists and belongs to user
        ad = self.db.query(Ad).filter(
            and_(Ad.id == request_data.ad_id, Ad.user_id == user.id)
        ).first()
        
        if not ad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ad not found or you don't have permission to request verification for this ad"
            )

        # Check if user is verified with OneID
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You must verify your identity with OneID before requesting gold verification"
            )

        # Check if there's already a pending request
        existing_request = self.db.query(GoldVerificationRequest).filter(
            and_(
                GoldVerificationRequest.ad_id == request_data.ad_id,
                GoldVerificationRequest.status == GoldVerificationStatus.pending
            )
        ).first()

        if existing_request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A gold verification request is already pending for this ad"
            )

        # Create new request
        verification_request = GoldVerificationRequest(
            ad_id=request_data.ad_id,
            requested_by=user.id,
            request_reason=request_data.request_reason,
            status=GoldVerificationStatus.pending
        )

        self.db.add(verification_request)
        self.db.commit()
        self.db.refresh(verification_request)
        return verification_request

    def get_pending_gold_requests(self) -> List[GoldVerificationRequest]:
        """
        Get all pending gold verification requests (admin only)
        """
        return self.db.query(GoldVerificationRequest).filter(
            GoldVerificationRequest.status == GoldVerificationStatus.pending
        ).all()

    def get_all_gold_requests(self) -> List[GoldVerificationRequest]:
        """
        Get all gold verification requests (admin only)
        """
        return self.db.query(GoldVerificationRequest).all()

    def process_gold_verification_request(
        self, 
        request_id: int, 
        update_data: GoldVerificationRequestUpdate, 
        admin_user: User
    ) -> GoldVerificationRequest:
        """
        Process a gold verification request (approve or reject)
        """
        verification_request = self.db.query(GoldVerificationRequest).filter(
            GoldVerificationRequest.id == request_id
        ).first()

        if not verification_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gold verification request not found"
            )

        if verification_request.status != GoldVerificationStatus.pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This request has already been processed"
            )

        # Update request
        verification_request.status = update_data.status
        verification_request.admin_comment = update_data.admin_comment
        verification_request.processed_by = admin_user.id
        verification_request.processed_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(verification_request)
        return verification_request

    def get_user_gold_requests(self, user: User) -> List[GoldVerificationRequest]:
        """
        Get all gold verification requests made by a user
        """
        return self.db.query(GoldVerificationRequest).filter(
            GoldVerificationRequest.requested_by == user.id
        ).all()

    def get_ad_gold_requests(self, ad_id: int) -> List[GoldVerificationRequest]:
        """
        Get all gold verification requests for a specific ad
        """
        return self.db.query(GoldVerificationRequest).filter(
            GoldVerificationRequest.ad_id == ad_id
        ).all()

    def cancel_gold_verification_request(
        self, 
        request_id: int, 
        user: User
    ) -> GoldVerificationRequest:
        """
        Cancel a pending gold verification request (only by the requester)
        """
        verification_request = self.db.query(GoldVerificationRequest).filter(
            and_(
                GoldVerificationRequest.id == request_id,
                GoldVerificationRequest.requested_by == user.id
            )
        ).first()

        if not verification_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gold verification request not found or you don't have permission to cancel it"
            )

        if verification_request.status != GoldVerificationStatus.pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending requests can be cancelled"
            )

        # Update request status
        verification_request.status = GoldVerificationStatus.rejected
        verification_request.admin_comment = "Cancelled by user"
        verification_request.processed_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(verification_request)
        return verification_request
