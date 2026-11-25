import pytest

@pytest.fixture
def valid_application_data():
    return {
        "company_name": "Google",
        "role_title": "Software Engineer",
        "date_applied": "2026-11-24",
        "location": "Remote"
    }

# retrieving empty applications
def test_get_applications_empty(client, auth_headers):
    # Act
    response = client.get("/applications", headers=auth_headers)
    # Assert
    assert response.status_code == 200
    assert response.json() == []

# testing successful application creation
def test_create_application_success(client, auth_headers, valid_application_data):
    # Act
    response = client.post("/applications", json=valid_application_data, headers=auth_headers)
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] is not None
    assert data["company"]["name"] == valid_application_data["company_name"].title()
    assert data["role_title"] == valid_application_data["role_title"]
    assert data["date_applied"] == valid_application_data["date_applied"]
    assert data["location"] == valid_application_data["location"]
    assert data["application_link"] is None
    assert data["current_status"] == "applied"

# testing retrieval of created applications
def test_get_applications_success(client, auth_headers, valid_application_data):
    # Arrange: Create an application
    response = client.post("/applications", json=valid_application_data, headers=auth_headers)
    assert response.status_code == 200
    created_application = response.json()

    # Act: Retrieve all applications
    response = client.get("/applications", headers=auth_headers)

    # Assert
    assert response.status_code == 200

    applications = response.json()
    assert len(applications) == 1

    application = applications[0]

    assert application["id"] == created_application["id"]
    assert application["company"]["name"] == valid_application_data["company_name"].title()
    assert application["role_title"] == valid_application_data["role_title"]
    assert application["date_applied"] == valid_application_data["date_applied"]
    assert application["location"] == valid_application_data["location"]
    assert application["application_link"] is None
    assert application["current_status"] == "applied"

# testing application status update
def test_update_application_status(client, auth_headers, valid_application_data):
    # Arrange: Create an application and retrieve its ID
    response = client.post("/applications", json=valid_application_data, headers=auth_headers)
    assert response.status_code == 200
    application_id = response.json()["id"]

    # Act: Update the application status
    response = client.patch(
        f"/applications/{application_id}/status",
        json={"status": "interviewing"},
        headers=auth_headers
    )

    # Assert: Verify the updated status
    assert response.status_code == 200
    updated_application = response.json()
    assert updated_application["id"] == application_id
    assert updated_application["current_status"] == "interviewing"

# updating a nonexistent application should return a 404 error
def test_update_nonexistent_application(client, auth_headers):
    # Act: Attempt to update an application that doesn't exist
    response = client.patch(
        "/applications/100000/status",
        json={"status": "interviewing"},
        headers=auth_headers
    )
    # Assert: Verify the request is rejected
    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"

# testing user data isolation
def test_application_data_isolation(client, create_authenticated_user, valid_application_data):
    # Arrange: Create two authenticated users
    user_a_headers = create_authenticated_user("user_a@example.com")
    user_b_headers = create_authenticated_user("user_b@example.com")
    # Arrange: Create an application as User A
    response = client.post("/applications", json=valid_application_data, headers=user_a_headers)
    assert response.status_code == 200
    # Act: Retrieve applications as User B
    response = client.get("/applications", headers=user_b_headers)
    # Assert: User B cannot see User A's application
    assert response.status_code == 200
    assert response.json() == []
    # Verify: User A can still retrieve their own application
    response = client.get("/applications", headers=user_a_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

# testing unauthorized status update attempt
def test_update_another_users_application(client, create_authenticated_user, valid_application_data):
    # Arrange: Create two authenticated users
    user_a_headers = create_authenticated_user("user_a@example.com")
    user_b_headers = create_authenticated_user("user_b@example.com")
    # Arrange: Create an application as User A
    response = client.post("/applications", json=valid_application_data, headers=user_a_headers)
    assert response.status_code == 200
    # Act: Attempt to update the application as User B
    application_id = response.json()["id"]
    response = client.patch(
        f"/applications/{application_id}/status",
        json={"status": "interviewing"},
        headers=user_b_headers
    )
    # Assert: Verify the request is rejected
    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"
    # Verify: Retrieve the application as User A and confirm its status remains unchanged
    response = client.get("/applications", headers=user_a_headers)
    assert response.status_code == 200
    assert response.json()[0]["current_status"] == "applied"