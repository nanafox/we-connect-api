from datetime import datetime
from uuid import uuid4

import sqlalchemy
from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from posts_app.database import Base
from posts_app.utils import UtilMixin


class Post(Base, UtilMixin):
    """Model for posts"""

    __tablename__ = "posts"

    id: Mapped[sqlalchemy.Uuid] = mapped_column(
        sqlalchemy.Uuid,
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid(),
        unique=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String, index=True)
    content: Mapped[str] = mapped_column(String, index=True)
    published: Mapped[bool] = mapped_column(Boolean, server_default="True")
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=datetime.now,
    )
    user_id: Mapped[sqlalchemy.Uuid] = mapped_column(
        sqlalchemy.Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    user: Mapped["User"] = relationship()

    def __str__(self):
        return f"Post title: {self.title}"


class User(Base, UtilMixin):
    """Model for users."""

    __tablename__ = "users"

    id: Mapped[sqlalchemy.Uuid] = mapped_column(
        sqlalchemy.Uuid,
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid(),
        unique=True,
        index=True,
    )
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[str] = mapped_column(String)
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        onupdate=datetime.now,
    )

    def __str__(self):
        return f"Email: {self.email}"


class Vote(Base, UtilMixin):
    """Model for votes."""

    __tablename__ = "votes"

    user_id: Mapped[sqlalchemy.Uuid] = mapped_column(
        sqlalchemy.Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    post_id: Mapped[sqlalchemy.Uuid] = mapped_column(
        sqlalchemy.Uuid,
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True,
    )
