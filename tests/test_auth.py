from fastapi.testclient import TestClient
from main import app
import pytest

@pytest.fixture
def valid_signup_data():
    return {
        "email": "test@example.com",
        "password": "fake_password"
    }


# successful user registration test
def test_signup_success(client, valid_signup_data):
    response = client.post("/signup", json=valid_signup_data)
    assert response.status_code == 200

    body = response.json()
    assert body["email"] == valid_signup_data["email"]
    assert body["id"] is not None
    assert "password" not in body
    assert "password_hash" not in body

# testing duplication of email registration
def test_duplicate_signup(client, valid_signup_data):
    # Arrange: Register the first user
    response = client.post("/signup", json=valid_signup_data)
    assert response.status_code == 200

    # Act: Attempt to register the same user again
    response = client.post("/signup", json=valid_signup_data)

    # Assert: Verify the request is rejected
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"