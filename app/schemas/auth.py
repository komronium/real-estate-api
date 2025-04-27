from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LoginAdminRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str
