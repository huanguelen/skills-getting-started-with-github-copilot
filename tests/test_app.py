"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirect(self):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_all_activities(self):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Verify each activity has required fields
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data

    def test_activities_have_expected_fields(self):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        activities = response.json()
        
        # Check a known activity
        assert "Chess Club" in activities
        chess_club = activities["Chess Club"]
        assert chess_club["max_participants"] == 12
        assert isinstance(chess_club["participants"], list)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_successful_signup(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Basketball Club" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_nonexistent_activity(self):
        """Test signup for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_duplicate_signup(self):
        """Test that duplicate signup is rejected"""
        email = "michael@mergington.edu"
        
        # Try to sign up someone already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_updates_participants_list(self):
        """Test that signup updates the participants list"""
        # Get initial state
        response1 = client.get("/activities")
        initial_count = len(response1.json()["Soccer Team"]["participants"])
        
        # Sign up for activity
        client.post(
            "/activities/Soccer Team/signup",
            params={"email": "test@mergington.edu"}
        )
        
        # Get updated state
        response2 = client.get("/activities")
        updated_count = len(response2.json()["Soccer Team"]["participants"])
        
        assert updated_count == initial_count + 1


class TestRemoveFromActivity:
    """Tests for the DELETE /activities/{activity_name}/signup endpoint"""

    def test_successful_removal(self):
        """Test successful removal from an activity"""
        response = client.delete(
            "/activities/Programming Class/signup",
            params={"email": "emma@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Programming Class" in data["message"]
        assert "emma@mergington.edu" in data["message"]

    def test_remove_nonexistent_activity(self):
        """Test removal from a non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_remove_not_signed_up(self):
        """Test that removing someone not signed up is rejected"""
        response = client.delete(
            "/activities/Art Club/signup",
            params={"email": "notsignedup@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()

    def test_removal_updates_participants_list(self):
        """Test that removal updates the participants list"""
        # Get initial state
        response1 = client.get("/activities")
        initial_count = len(response1.json()["Gym Class"]["participants"])
        
        # Remove a participant
        client.delete(
            "/activities/Gym Class/signup",
            params={"email": "john@mergington.edu"}
        )
        
        # Get updated state
        response2 = client.get("/activities")
        updated_count = len(response2.json()["Gym Class"]["participants"])
        
        assert updated_count == initial_count - 1