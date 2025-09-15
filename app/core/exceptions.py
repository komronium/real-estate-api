"""
Custom exceptions for the Real Estate API
"""
from typing import Any, Dict, Optional


class RealEstateException(Exception):
    """Base exception for Real Estate API"""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(RealEstateException):
    """Raised when data validation fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class NotFoundError(RealEstateException):
    """Raised when a resource is not found"""
    def __init__(self, message: str, resource_type: str = "Resource"):
        super().__init__(message, status_code=404, details={"resource_type": resource_type})


class AuthenticationError(RealEstateException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationError(RealEstateException):
    """Raised when authorization fails"""
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message, status_code=403)


class DatabaseError(RealEstateException):
    """Raised when database operations fail"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        details = {"original_error": str(original_error)} if original_error else {}
        super().__init__(message, status_code=500, details=details)


class ExternalServiceError(RealEstateException):
    """Raised when external service calls fail"""
    def __init__(self, message: str, service_name: str, status_code: int = 500):
        super().__init__(message, status_code, details={"service_name": service_name})
