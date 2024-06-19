import subprocess

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from posts_app.api.main import app
from posts_app.config import settings
from posts_app.database import Base, get_db


@pytest.fixture(scope="package", autouse=True)
def setup_teardown_test_db():
    print("Setting up")
    # Run setup script before tests
    subprocess.run(["./setup_test_db.sh"])

    # Yield to run the tests
    yield

    # Run teardown script after tests
    subprocess.run(["./teardown_test_db.sh"])


@pytest.fixture(scope="session")
def session():
    engine = create_engine(
        "postgresql://"
        f"{settings.db_user}:{settings.db_password}@"
        f"localhost/{settings.db_name}_test"
    )

    TestDBSession = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestDBSession()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def api_client(session: Session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)
