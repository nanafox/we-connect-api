from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from posts_app.config import settings

SQLALCHEMY_DATABASE_URL = (
    "postgresql://"
    f"{settings.db_user}:{settings.db_password}"
    f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

DBSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()
