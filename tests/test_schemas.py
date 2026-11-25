from schemas import ApplicationCreate
from datetime import date
from pydantic import ValidationError
import pytest

# TC-001 | Positive Unit Test
# Verify that valid application data is accepted
def test_create_valid_application():
    # Arrange
    data = {
        "company_name": "Google",
        "role_title": "Software Engineer",
        "date_applied": "2026-11-24",
        "location": "Remote"
    }

    # Act
    application = ApplicationCreate(**data)

    # Assert
    assert application.company_name == "Google"
    assert application.role_title == "Software Engineer"
    assert application.date_applied == date(2026, 11, 24)
    assert application.location == "Remote"
    assert application.application_link is None
    assert application.current_status == "applied"

# TC-002 | Negative Unit Test
# Verify that invalid application data is rejected
def test_missing_company_name():
    # Arrange
    data = {
        "role_title": "Software Engineer",
        "date_applied": "2026-11-24",
        "location": "Remote",
    }
    with pytest.raises(ValidationError):
        ApplicationCreate(**data)

# TC-003 | Negative Unit Test
# Verify invalid application date 
def test_invalid_date():
    # Arrange
    data = {
        "company_name": "Google",
        "role_title": "Software Engineer",
        "date_applied": "invalid-date",
        "location": "Remote",
    }

    # Act
    with pytest.raises(ValidationError) as exc_info:
        ApplicationCreate(**data)

    # Assert
    errors = exc_info.value.errors()

    assert any(
        error["loc"] == ("date_applied",)
        for error in errors
    )

# TC-004 | Negative Unit Test
# verify an empty company name is rejected
def test_empty_company_name():
    # Arrange
    data = {
        "company_name": "",
        "role_title": "Software Engineer",
        "date_applied": "2026-11-24",
        "location": "Remote",
    }

    # Act
    with pytest.raises(ValidationError) as exc_info:
        ApplicationCreate(**data)

    # Assert
    errors = exc_info.value.errors()

    assert any(
        error["loc"] == ("company_name",)
        for error in errors
    )
