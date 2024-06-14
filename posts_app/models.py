from datetime import datetime
from uuid import uuid4

import sqlalchemy
from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    ForeignKey,
    String,
    func,
    text,
)
from sqlalchemy.orm import relationship

from posts_app.database import Base
from posts_app.utils import UtilMixin


class Post(Base, UtilMixin):
    """Model for Posts"""

    __tablename__ = "posts"

    id = Column(
        sqlalchemy.Uuid,
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid(),
        unique=True,
        index=True,
    )
    title = Column(String, index=True, nullable=False)
    content = Column(String, nullable=False, index=True)
    published = Column(Boolean, server_default="True", nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=datetime.now,
    )
    user_id = Column(
        sqlalchemy.Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    user = relationship("User")

    def __str__(self):
        return f"Post title: {self.title}"


class User(Base, UtilMixin):
    __tablename__ = "users"

    id = Column(
        sqlalchemy.Uuid,
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid(),
        unique=True,
        index=True,
    )
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=datetime.now,
    )

    def __str__(self):
        return f"Email: {self.email}"


class Vote(Base, UtilMixin):
    __tablename__ = "votes"

    user_id = Column(
        sqlalchemy.Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    post_id = Column(
        sqlalchemy.Uuid,
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True,
    )
