"""
Tests for the Mergington High School Activities API
"""

import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


class TestActivitiesEndpoints:
    """Tests for activities endpoints"""

    def test_get_activities(self):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_activity_structure(self):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_signup_for_activity(self):
        """Test signing up for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=test@example.com"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@example.com" in data["message"]

    def test_signup_already_registered(self):
        """Test that signing up twice fails"""
        email = "duplicate@example.com"
        
        # First signup
        response1 = client.post(
            f"/activities/Tennis Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            f"/activities/Tennis Club/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_nonexistent_activity(self):
        """Test signing up for an activity that doesn't exist"""
        response = client.post(
            "/activities/Fake Activity/signup?email=test@example.com"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_from_activity(self):
        """Test unregistering from an activity"""
        email = "unregister@example.com"
        
        # First sign up
        signup_response = client.post(
            f"/activities/Drama Club/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Then unregister
        unregister_response = client.post(
            f"/activities/Drama Club/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        data = unregister_response.json()
        assert "message" in data
        assert email in data["message"]

    def test_unregister_not_registered(self):
        """Test unregistering from an activity when not registered"""
        response = client.post(
            "/activities/Art Studio/unregister?email=notregistered@example.com"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_nonexistent_activity(self):
        """Test unregistering from an activity that doesn't exist"""
        response = client.post(
            "/activities/Fake Activity/unregister?email=test@example.com"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_participant_count(self):
        """Test that participants are properly counted"""
        response = client.get("/activities")
        data = response.json()
        
        # Check that each activity has the expected participant structure
        for activity_name, activity_data in data.items():
            participants = activity_data["participants"]
            assert len(participants) <= activity_data["max_participants"]


class TestRootEndpoint:
    """Tests for root endpoint"""

    def test_root_redirect(self):
        """Test that root redirects to static files"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
