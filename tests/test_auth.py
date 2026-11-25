from fastapi.testclient import TestClient
from main import app
import pytest
from models import User
from auth import verify_password

# successful user registration test
def test_signup_success(client, valid_signup_data):
    response = client.post("/signup", json=valid_signup_data)
    assert response.status_code == 200

    body = response.json()
    assert body["email"] == valid_signup_data["email"]
    assert body["id"] is not None
    # ensuring valid credientials are not returned in the response
    assert "password" not in body
    assert "password_hash" not in body

# testing duplication of email registration
def test_duplicate_signup(client, valid_signup_data):
    # Arrange: Register the first user
    first_response = client.post("/signup", json=valid_signup_data)
    assert first_response.status_code == 200

    # Act: Attempt to register the same user again
    duplicate_response = client.post("/signup", json=valid_signup_data)

    # Assert: Verify the request is rejected
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Email already registered"

# testing invalid email format during registration
def test_signup_invalid_email(client, valid_signup_data):
    # Arrange
    invalid_data = valid_signup_data.copy()
    invalid_data["email"] = "invalid-email-format"

    # Act
    response = client.post("/signup", json=invalid_data)

    # Assert
    assert response.status_code == 422  # Unprocessable Entity
    assert "value is not a valid email address" in response.text

# testing missing required password field during registration
def test_signup_missing_password(client, valid_signup_data):
    # Arrange
    invalid_data = valid_signup_data.copy()
    del invalid_data["password"]

    # Act
    response = client.post("/signup", json=invalid_data)

    # Assert
    assert response.status_code == 422
    assert "field required" in response.text.lower()

# testing a successful login
def test_login_success(client, valid_signup_data):
    # Arrange (register user first)
    signup_response = client.post("/signup", json=valid_signup_data)
    assert signup_response.status_code == 200
    # Act (login attempt)
    response = client.post("/login", json=valid_signup_data)
    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] 
    assert body["token_type"] == "bearer"

# testing incorrect password during login
def test_login_incorrect_password(client, valid_signup_data):
    # Arrange (register user)
    signup_response = client.post("/signup", json=valid_signup_data)
    assert signup_response.status_code == 200
    # Act (login with wrong password)
    invalid_data = valid_signup_data.copy()
    invalid_data["password"] = "wrong_password"
    response = client.post("/login", json=invalid_data)
    # Assert    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
    assert "access_token" not in response.json()

# testing unregistered email during login
def test_login_unregistered_email(client, valid_signup_data):
    # Act (login with unregistered email)
    invalid_data = valid_signup_data.copy()
    invalid_data["email"] = "unregistered@example.com"
    response = client.post("/login", json=invalid_data)
    # Assert
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
    assert "access_token" not in response.json()

# testing password hashing
def test_signup_password_hashing(client, valid_signup_data, db_session):
    # Arrange: Register a user
    response = client.post("/signup", json=valid_signup_data)
    assert response.status_code == 200
    user_id = response.json()["id"]

    # Act: Retrieve the user from the database
    user = db_session.query(User).filter(User.id == user_id).first()

    assert user.email == valid_signup_data["email"]
    # Assert: Verify the user exists
    assert user is not None
    # Assert: Verify the password is not stored as plaintext
    assert user.password_hash != valid_signup_data["password"]
    # Assert: Verify the stored hash matches the original password
    assert verify_password(valid_signup_data["password"], user.password_hash)

# testing retrieval of current user information
def test_get_current_user(client, valid_signup_data):
    # Arrange: Register a user
    signup_response = client.post("/signup", json=valid_signup_data)
    assert signup_response.status_code == 200
    # Arrange: Log in and retrieve the access token
    login_response = client.post("/login", json=valid_signup_data)
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]
    # Arrange: Construct authorization headers
    headers = {"Authorization": f"Bearer {access_token}"}
    # Act: Send GET request to /me
    response = client.get("/me", headers=headers)
    # Assert: Verify status code and user information
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == valid_signup_data["email"]
    assert body["id"] == signup_response.json()["id"]
    assert "access_token" not in body
    assert "password" not in body
    assert "password_hash" not in body

# testing retrieval without authorization header
def test_get_current_user_no_token(client):
    # Act
    response = client.get("/me")

    # Assert
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

# testing retrieval of current user information with invalid token
def test_get_current_user_invalid_token(client):
    # Arrange: Construct authorization headers (incorrect)
    headers = {"Authorization": "Bearer invalid_token"}
    # Act: Send GET request to /me with invalid token
    response = client.get("/me", headers=headers)
    # Assert: Verify status code and error message
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"