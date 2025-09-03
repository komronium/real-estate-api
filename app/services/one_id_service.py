import httpx
import logging
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode, quote
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User, OneIDInfo
from app.schemas.one_id import (
    OneIDUserInfo,
    OneIDLegalInfo,
    OneIDTokenResponse
)

logger = logging.getLogger(__name__)


class OneIDService:
    """Service for handling One ID (Yagona identifikatsiya tizimi) integration"""
    
    def __init__(self, db: Session):
        self.db = db
        self.base_url = "https://sso.egov.uz/sso/oauth"
        self.client_id = settings.ONE_ID_CLIENT_ID
        self.client_secret = settings.ONE_ID_CLIENT_SECRET
        self.redirect_uri = settings.ONE_ID_REDIRECT_URI
        self.scope = settings.ONE_ID_SCOPE

    async def exchange_code_for_token(self, code: str) -> OneIDTokenResponse:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from One ID
            
        Returns:
            Token response with access_token and refresh_token
        """
        async with httpx.AsyncClient() as client:
            params = {
                "grant_type": "one_authorization_code",
                "client_id": self.client_id,
                "client_secret": self.client_secret.get_secret_value(),
                "redirect_uri": self.redirect_uri,
                "code": code
            }
            
            try:
                response = await client.post(
                    f"{self.base_url}/Authorization.do",
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                
                token_data = response.json()
                return OneIDTokenResponse(**token_data)
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error exchanging code for token: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange authorization code for token"
                )
            except Exception as e:
                logger.error(f"Error exchanging code for token: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error during token exchange"
                )

    async def get_user_info(self, access_token: str) -> OneIDUserInfo:
        """
        Get user information using access token
        
        Args:
            access_token: Valid access token from One ID
            
        Returns:
            User information from One ID
        """
        async with httpx.AsyncClient() as client:
            params = {
                "grant_type": "one_access_token_identify",
                "client_id": self.client_id,
                "client_secret": self.client_secret.get_secret_value(),
                "access_token": access_token,
                "scope": self.scope
            }
            
            try:
                response = await client.post(
                    f"{self.base_url}/Authorization.do",
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                
                user_data = response.json()
                return OneIDUserInfo(**user_data)
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error getting user info: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user information"
                )
            except Exception as e:
                logger.error(f"Error getting user info: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error getting user information"
                )

    async def logout_user(self, access_token: str) -> bool:
        """
        Logout user from One ID system
        
        Args:
            access_token: Valid access token from One ID
            
        Returns:
            True if logout successful
        """
        async with httpx.AsyncClient() as client:
            params = {
                "grant_type": "one_log_out",
                "client_id": self.client_id,
                "client_secret": self.client_secret.get_secret_value(),
                "access_token": access_token,
                "scope": self.scope
            }
            
            try:
                response = await client.post(
                    f"{self.base_url}/Authorization.do",
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                
                return True
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error during logout: {e}")
                return False
            except Exception as e:
                logger.error(f"Error during logout: {e}")
                return False

    def update_current_user_with_one_id(self, current_user: User, one_id_user: OneIDUserInfo) -> User:
        """
        Update current user with One ID information
        
        Args:
            current_user: Current authenticated user
            one_id_user: User information from One ID
            
        Returns:
            Updated user object from database
        """
        # Check if One ID info already exists for this user
        one_id_info = self.db.query(OneIDInfo).filter(OneIDInfo.user_id == current_user.id).first()
        
        # Check if this One ID user_id is already used by another user
        existing_one_id = self.db.query(OneIDInfo).filter(
            OneIDInfo.one_id_user_id == one_id_user.user_id,
            OneIDInfo.user_id != current_user.id
        ).first()
        
        if existing_one_id:
            # This One ID is already linked to another user, update that user's info
            existing_one_id.pin = one_id_user.pin
            existing_one_id.full_name = one_id_user.full_name
            existing_one_id.first_name = one_id_user.first_name
            existing_one_id.last_name = one_id_user.sur_name
            existing_one_id.middle_name = one_id_user.mid_name
            existing_one_id.passport_number = one_id_user.pport_no
            existing_one_id.birth_date = one_id_user.birth_date
            existing_one_id.user_type = one_id_user.user_type
            existing_one_id.is_verified = one_id_user.valid
            existing_one_id.one_id_session_id = one_id_user.sess_id
            existing_one_id.validation_method = ",".join(one_id_user.validation_method) if one_id_user.validation_method else None
            existing_one_id.auth_method = one_id_user.auth_method
            existing_one_id.pkcs_legal_tin = one_id_user.pkcs_legal_tin
            
            # Return the user that owns this One ID
            return existing_one_id.user
        
        if one_id_info:
            # Update existing One ID info for current user
            one_id_info.pin = one_id_user.pin
            one_id_info.full_name = one_id_user.full_name
            one_id_info.first_name = one_id_user.first_name
            one_id_info.last_name = one_id_user.sur_name
            one_id_info.middle_name = one_id_user.mid_name
            one_id_info.passport_number = one_id_user.pport_no
            one_id_info.birth_date = one_id_user.birth_date
            one_id_info.user_type = one_id_user.user_type
            one_id_info.is_verified = one_id_user.valid
            one_id_info.one_id_user_id = one_id_user.user_id
            one_id_info.one_id_session_id = one_id_user.sess_id
            one_id_info.validation_method = ",".join(one_id_user.validation_method) if one_id_user.validation_method else None
            one_id_info.auth_method = one_id_user.auth_method
            one_id_info.pkcs_legal_tin = one_id_user.pkcs_legal_tin
        else:
            # Create new One ID info for current user
            one_id_info = OneIDInfo(
                user_id=current_user.id,
                pin=one_id_user.pin,
                full_name=one_id_user.full_name,
                first_name=one_id_user.first_name,
                last_name=one_id_user.sur_name,
                middle_name=one_id_user.mid_name,
                passport_number=one_id_user.pport_no,
                birth_date=one_id_user.birth_date,
                user_type=one_id_user.user_type,
                is_verified=one_id_user.valid,
                one_id_user_id=one_id_user.user_id,
                one_id_session_id=one_id_user.sess_id,
                validation_method=",".join(one_id_user.validation_method) if one_id_user.validation_method else None,
                auth_method=one_id_user.auth_method,
                pkcs_legal_tin=one_id_user.pkcs_legal_tin
            )
            self.db.add(one_id_info)
        
        # Update user name if not set
        if not current_user.name:
            current_user.name = one_id_user.full_name
        
        self.db.commit()
        self.db.refresh(current_user)
        self.db.refresh(one_id_info)
        return current_user

    def get_user_by_one_id(self, one_id_user_id: str) -> Optional[User]:
        """
        Get user by One ID user ID
        
        Args:
            one_id_user_id: One ID user identifier
            
        Returns:
            User object if found, None otherwise
        """
        one_id_info = self.db.query(OneIDInfo).filter(OneIDInfo.one_id_user_id == one_id_user_id).first()
        return one_id_info.user if one_id_info else None

    def get_user_by_pin(self, pin: str) -> Optional[User]:
        """
        Get user by PIN (JShShIR)
        
        Args:
            pin: Personal identification number
            
        Returns:
            User object if found, None otherwise
        """
        one_id_info = self.db.query(OneIDInfo).filter(OneIDInfo.pin == pin).first()
        return one_id_info.user if one_id_info else None
