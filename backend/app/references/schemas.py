from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# General Fields
class ReferenceOption(BaseModel):
    id: Optional[int] = None
    name: str
    type: str
    is_default: bool
    is_frequent: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReferenceOptionUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    is_default: Optional[bool] = None
    is_frequent: Optional[bool] = None
    updated_at: Optional[datetime] = None


# General Fields
class ReferenceTemplate(BaseModel):
    id: Optional[int] = None
    name: str
    type: str
    is_default: bool
    content: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReferenceTemplateUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    is_default: Optional[bool] = None
    content: Optional[str] = None
    is_frequent: Optional[bool] = None
    updated_at: Optional[datetime] = None
