from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import EmailStr
from pydantic import BaseModel, HttpUrl


class PostBase(BaseModel):
    """Base schema for posts."""

    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


class Post(PostBase):
    """Schema for displaying a single post response"""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PostCreateUpdate(PostBase):
    """Schema for creating and updating posts."""

    pass


class PostPartialUpdate(BaseModel):
    """Schema for updating a post partially."""

    title: str | None = None
    content: str | None = None
    published: bool = True
    rating: Optional[int] = None


class Link(BaseModel):
    next: Optional[HttpUrl]
    previous: Optional[HttpUrl]


class MetaData(BaseModel):
    links: Link
    status_code: int
    count: int
    total_pages: int
    current_page: int


class PostsList(BaseModel):
    """Schema for the response of posts."""

    data: List[Post]
    metadata: MetaData


class UserBase(BaseModel):
    email: EmailStr


class UserCreateUpdate(UserBase):
    password: str


class User(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StatusResponse(BaseModel):
    status: str = "OK"
