from posts_app.database import Base
from sqlalchemy import Column, String, Boolean, Integer, DateTime
from datetime import datetime
from uuid import uuid4


class Post(Base):
    __tablename__ = "posts"

    id = Column(
        String,
        primary_key=True,
        index=True,
        default=str(uuid4()),
        nullable=False,
        unique=True,
    )
    title = Column(String, index=True, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, default=True, nullable=False)
    rating = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    def __str__(self):
        return f"Post title: {self.title}"
