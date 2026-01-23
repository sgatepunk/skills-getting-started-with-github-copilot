"""
Test suite for the Mergington High School Activity Management API

Tests cover all API endpoints and their error handling.
"""

import pytest
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    
    # Store original state
    original_state = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and games",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and compete in matches",
            "schedule": "Tuesdays and Saturdays, 3:00 PM - 4:30 PM",
            "max_participants": 10,
            "participants": ["james@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act in plays and develop theatrical performance skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Design and build robots for competitions",
            "schedule": "Tuesdays, Thursdays, and Saturdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["ethan@mergington.edu"]
        }
    }
    
    # Clear activities
    activities.clear()
    # Restore original state
    activities.update(original_state)
    
    yield
    
    # Restore after test
    activities.clear()
    activities.update(original_state)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert len(data) == 9
    
    def test_get_activities_returns_activity_details(self, client, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_get_activities_participants_list(self, client, reset_activities):
        """Test that participants are correctly listed"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_successfully(self, client, reset_activities):
        """Test successfully signing up a new participant"""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_participant_appears_in_activity(self, client, reset_activities):
        """Test that signed up participant appears in activity"""
        # Sign up a new participant
        client.post(
            "/activities/Tennis%20Club/signup",
            params={"email": "newtennis@mergington.edu"}
        )
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        assert "newtennis@mergington.edu" in data["Tennis Club"]["participants"]
    
    def test_signup_duplicate_participant_fails(self, client, reset_activities):
        """Test that duplicate signup is rejected"""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signup to non-existent activity fails"""
        response = client.post(
            "/activities/Fake%20Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_increases_participant_count(self, client, reset_activities):
        """Test that signup increases the participant count"""
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Art Studio"]["participants"])
        
        # Sign up a new participant
        client.post(
            "/activities/Art%20Studio/signup",
            params={"email": "newartist@mergington.edu"}
        )
        
        # Check new count
        response = client.get("/activities")
        new_count = len(response.json()["Art Studio"]["participants"])
        
        assert new_count == initial_count + 1


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant_successfully(self, client, reset_activities):
        """Test successfully unregistering an existing participant"""
        response = client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]
    
    def test_unregister_participant_removed_from_activity(self, client, reset_activities):
        """Test that unregistered participant no longer appears in activity"""
        # Unregister a participant
        client.delete(
            "/activities/Robotics%20Club/unregister",
            params={"email": "ethan@mergington.edu"}
        )
        
        # Verify participant was removed
        response = client.get("/activities")
        data = response.json()
        assert "ethan@mergington.edu" not in data["Robotics Club"]["participants"]
    
    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """Test that unregistering a non-participating student fails"""
        response = client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        """Test that unregistering from non-existent activity fails"""
        response = client.delete(
            "/activities/Fake%20Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_decreases_participant_count(self, client, reset_activities):
        """Test that unregister decreases the participant count"""
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        # Unregister a participant
        client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        
        # Check new count
        response = client.get("/activities")
        new_count = len(response.json()["Chess Club"]["participants"])
        
        assert new_count == initial_count - 1


class TestIntegrationScenarios:
    """Integration tests for complex scenarios"""
    
    def test_signup_then_unregister_participant(self, client, reset_activities):
        """Test signup followed by unregister"""
        email = "testuser@mergington.edu"
        activity = "Programming%20Class"
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        assert email in response.json()["Programming Class"]["participants"]
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister", params={"email": email})
        assert response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        assert email not in response.json()["Programming Class"]["participants"]
    
    def test_multiple_signups_different_activities(self, client, reset_activities):
        """Test signing up for multiple activities"""
        email = "multijoiner@mergington.edu"
        activities = ["Chess%20Club", "Drama%20Club", "Tennis%20Club"]
        
        # Sign up for multiple activities
        for activity in activities:
            response = client.post(f"/activities/{activity}/signup", params={"email": email})
            assert response.status_code == 200
        
        # Verify all signups
        response = client.get("/activities")
        data = response.json()
        for activity_key in ["Chess Club", "Drama Club", "Tennis Club"]:
            assert email in data[activity_key]["participants"]
    
    def test_signup_then_duplicate_signup_fails(self, client, reset_activities):
        """Test that duplicate signup is rejected after successful signup"""
        email = "testuser@mergington.edu"
        
        # First signup should succeed
        response = client.post(
            "/activities/Gym%20Class/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Second signup with same email should fail
        response = client.post(
            "/activities/Gym%20Class/signup",
            params={"email": email}
        )
        assert response.status_code == 400
