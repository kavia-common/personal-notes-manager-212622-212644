from pydantic import BaseModel, Field
from typing import Optional
from pydantic import ConfigDict


# PUBLIC_INTERFACE
class NoteBase(BaseModel):
    """
    Base note schema.
    """
    title: str = Field(..., min_length=1, max_length=255, description="Note title")
    content: Optional[str] = Field(default=None, description="Note content")


# PUBLIC_INTERFACE
class NoteCreate(NoteBase):
    """
    Create note payload.
    """
    pass


# PUBLIC_INTERFACE
class NoteUpdate(BaseModel):
    """
    Update note payload.
    """
    title: Optional[str] = Field(default=None, min_length=1, max_length=255, description="New note title")
    content: Optional[str] = Field(default=None, description="New note content")


# PUBLIC_INTERFACE
class NoteOut(NoteBase):
    """
    Note representation for API responses.
    """
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="Note ID")
    owner_id: int = Field(..., description="Owner user ID")
