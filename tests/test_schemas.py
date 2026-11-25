from schemas import ApplicationCreate
from datetime import date
from pydantic import ValidationError
import pytest

@pytest.fixture
def valid_application_data():
    return {
        "company_name": "Google",
        "role_title": "Software Engineer",
        "date_applied": "2026-11-24",
    }

# Positive Unit Test
# Verify that valid application data is accepted
def test_create_valid_application(valid_application_data):
    # Act
    application = ApplicationCreate(**valid_application_data)

    # Assert
    assert application.company_name == "Google"
    assert application.role_title == "Software Engineer"
    assert application.date_applied == date(2026, 11, 24)
    assert application.location is None
    assert application.application_link is None
    assert application.current_status == "applied"

# Negative Unit Test
# Verify that invalid application data is rejected
def test_missing_company_name(valid_application_data):
    # Arrange
    valid_application_data["company_name"] = ""
    with pytest.raises(ValidationError):
        ApplicationCreate(**valid_application_data)

# Negative Unit Test
# Verify invalid application date 
def test_invalid_date(valid_application_data):
    # Arrange
    valid_application_data["date_applied"] = "invalid-date"

    with pytest.raises(ValidationError) as exc_info:
        ApplicationCreate(**valid_application_data)
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("date_applied",)
        for error in errors
    )

# Negative Unit Test
# verify an invalid company name is rejected
@pytest.mark.parametrize("company_name", [
    "",
    " "
])
def test_invalid_company_name(
    valid_application_data,
    company_name
):
    # Arrange
    valid_application_data["company_name"] = company_name

    # Act
    with pytest.raises(ValidationError) as exc_info:
        ApplicationCreate(**valid_application_data)

    # Assert
    errors = exc_info.value.errors()

    assert any(
        error["loc"] == ("company_name",)
        for error in errors
    )

# Positive Unit Test
# Verify surrounding whitespace is removed
@pytest.mark.parametrize(
    "input_name, expected_name",
    [
        ("   Google   ", "Google"),
        (" Google", "Google"),
        ("Google ", "Google"),
        ("Goldman Sachs", "Goldman Sachs"),
        ("A", "A"),
    ]
)
def test_whitespace_removal(input_name, expected_name):
    data = {
        "company_name": input_name,
        "role_title": "   Software Engineer   ",
        "date_applied": "2026-11-24",
    }
    application = ApplicationCreate(**data)
    assert application.company_name == expected_name
    assert application.role_title == "Software Engineer"