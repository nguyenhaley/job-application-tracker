import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from database import Base
import models
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from main import app
from main import get_db as main_get_db
from auth import get_db as auth_get_db

@pytest.fixture
def test_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    try:
        Base.metadata.create_all(bind=engine)
        yield engine
    finally:
        engine.dispose()

@pytest.fixture
def testing_session_factory(test_engine):
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )

@pytest.fixture
def db_session(testing_session_factory):
    db = testing_session_factory()

    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(testing_session_factory):
    def override_get_db():
        # Create a test database session
        db = testing_session_factory()
        # Yield the session
        try:
            yield db
        # Close the session afterward
        finally:
            db.close()

    app.dependency_overrides[main_get_db] = override_get_db
    app.dependency_overrides[auth_get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(main_get_db, None)
        app.dependency_overrides.pop(auth_get_db, None)