from sqlalchemy import inspect
from models import User
from main import app, get_db as main_get_db
from auth import get_db as auth_get_db

def test_database_overrides(client):
    assert main_get_db in app.dependency_overrides
    assert auth_get_db in app.dependency_overrides

def test_database_tables(test_engine):
    inspector = inspect(test_engine)
    tables = inspector.get_table_names()
    assert "users" in tables
    assert "companies" in tables
    assert "applications" in tables
    assert "status_history" in tables

# verify a user can be stored and retrieved from the database
def test_create_user(db_session):
    user = User(
        email="test@example.com", 
        password_hash="fake_hash"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    saved_user = db_session.query(User).filter(
        User.email == "test@example.com"
    ).first()

    assert saved_user is not None
    assert saved_user.id == user.id
    assert saved_user.email == "test@example.com"