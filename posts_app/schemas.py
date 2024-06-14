from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, HttpUrl


class PostBase(BaseModel):
    """Base schema for posts."""

    title: str
    content: str
    published: bool = True


class Post(PostBase):
    """Schema for displaying a single post response"""

    id: UUID
    created_at: datetime
    updated_at: datetime
    user: "PostOwner"

    class Config:
        from_attributes = True


class PostResponse(BaseModel):
    """
    Schema for displaying a single post response with votes.
    """
    post: Post
    votes: int


class PostCreateUpdate(PostBase):
    """Schema for creating and updating posts."""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "How to create a REST API",
                    "content": "This is a tutorial on how to create a REST API "
                    "using FastAPI.",
                    "published": False,
                },
                {
                    "title": "Getting Started with query parameters",
                    "content": "This tutorial will take you through the basics "
                    "of query parameters. Stay tuned.",
                },
            ]
        }
    }


class PostPartialUpdate(BaseModel):
    """Schema for updating a post partially."""

    title: str | None = None
    content: str | None = None
    published: bool = True


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

    data: List[PostResponse]
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


class UserLogin(UserCreateUpdate):
    pass


class Token(BaseModel):
    """
    Schema for the token response.

    - **access_token**: The token to be used for authentication.
    - **token_type**: The type of token.
    - **expire_in**: The time in minutes the token will expire.
    """

    access_token: str
    token_type: str = "bearer"
    expire_in: datetime


class TokenData(BaseModel):
    id: UUID
    email: EmailStr


class Vote(BaseModel):
    post_id: UUID
    status: bool


class PostOwner(BaseModel):
    email: EmailStr
    id: UUID
