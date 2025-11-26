from pydantic import BaseModel, Field
from pydantic import ConfigDict


# PUBLIC_INTERFACE
class UserBase(BaseModel):
    """
    Base user schema.
    """
    username: str = Field(..., min_length=3, max_length=191, description="Unique username")


# PUBLIC_INTERFACE
class UserCreate(UserBase):
    """
    Schema for creating a user.
    """
    password: str = Field(..., min_length=6, description="Password")


# PUBLIC_INTERFACE
class UserOut(UserBase):
    """
    Public user representation.
    """
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="User ID")
