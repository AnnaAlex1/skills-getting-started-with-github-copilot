import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy


@pytest.fixture
def client():
    """Fixture to provide a TestClient for the FastAPI app."""
    return TestClient(app, follow_redirects=False)


@pytest.fixture(autouse=True)
def reset_activities():
    """Fixture to reset activities data before each test."""
    # Store original data
    original_activities = copy.deepcopy(activities)
    yield
    # Reset after test
    activities.clear()
    activities.update(original_activities)


def test_root_redirect(client):
    """Test GET / redirects to static index.html."""
    # Arrange
    # (No special setup needed)

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test GET /activities returns the activities dictionary."""
    # Arrange
    # (Activities are set up by fixture)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert data["Chess Club"]["max_participants"] == 12


def test_signup_success(client):
    """Test POST /activities/{activity}/signup successfully adds a participant."""
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert email in activities[activity_name]["participants"]


def test_signup_activity_not_found(client):
    """Test POST /activities/{activity}/signup with invalid activity."""
    # Arrange
    invalid_activity = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{invalid_activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_duplicate_participant(client):
    """Test POST /activities/{activity}/signup prevents duplicate signups."""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_remove_participant_success(client):
    """Test DELETE /activities/{activity}/participants successfully removes a participant."""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Exists in participants

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_activity_not_found(client):
    """Test DELETE /activities/{activity}/participants with invalid activity."""
    # Arrange
    invalid_activity = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{invalid_activity}/participants?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_remove_participant_not_found(client):
    """Test DELETE /activities/{activity}/participants with non-existent participant."""
    # Arrange
    activity_name = "Chess Club"
    email = "nonexistent@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Participant not found" in data["detail"]