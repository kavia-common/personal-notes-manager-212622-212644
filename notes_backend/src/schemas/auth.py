from pydantic import BaseModel, Field


# PUBLIC_INTERFACE
class Token(BaseModel):
    """
    OAuth token response.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type, e.g., bearer")


# PUBLIC_INTERFACE
class TokenPayload(BaseModel):
    """
    Decoded JWT payload.
    """
    sub: str = Field(..., description="Subject (user id)")
    username: str = Field(..., description="Username")
