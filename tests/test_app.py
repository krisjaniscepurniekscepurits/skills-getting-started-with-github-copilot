"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""

    def test_get_activities(self):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        assert "Chess Club" in activities
        assert "Programming Class" in activities

    def test_activity_structure(self):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for the /signup endpoint"""

    def test_signup_for_activity_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=test@example.com",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "test@example.com" in result["message"]

    def test_signup_nonexistent_activity(self):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@example.com",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_student(self):
        """Test that a student cannot sign up twice for the same activity"""
        email = "duplicate@example.com"
        activity = "Chess Club"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/{activity}/signup?email={email}",
            headers={"Content-Type": "application/json"}
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/{activity}/signup?email={email}",
            headers={"Content-Type": "application/json"}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_updates_participants(self):
        """Test that signup updates the participants list"""
        email = "newstudent@example.com"
        activity = "Programming Class"
        
        # Get initial participant count
        response1 = client.get("/activities")
        initial_count = len(response1.json()[activity]["participants"])
        
        # Sign up
        response2 = client.post(
            f"/activities/{activity}/signup?email={email}",
            headers={"Content-Type": "application/json"}
        )
        assert response2.status_code == 200
        
        # Check updated participant count
        response3 = client.get("/activities")
        new_count = len(response3.json()[activity]["participants"])
        assert new_count == initial_count + 1
        assert email in response3.json()[activity]["participants"]


class TestUnregisterEndpoint:
    """Tests for the /unregister endpoint"""

    def test_unregister_success(self):
        """Test successful unregistration from an activity"""
        email = "unregister@example.com"
        activity = "Soccer Team"
        
        # Sign up first
        client.post(
            f"/activities/{activity}/signup?email={email}",
            headers={"Content-Type": "application/json"}
        )
        
        # Unregister
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]

    def test_unregister_nonexistent_activity(self):
        """Test unregistration from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=test@example.com"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_signed_up(self):
        """Test unregistration when student is not signed up"""
        response = client.delete(
            "/activities/Basketball Club/unregister?email=notregistered@example.com"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_removes_participant(self):
        """Test that unregistration removes the participant from the list"""
        email = "removetest@example.com"
        activity = "Art Workshop"
        
        # Sign up
        client.post(
            f"/activities/{activity}/signup?email={email}",
            headers={"Content-Type": "application/json"}
        )
        
        # Get initial participant count
        response1 = client.get("/activities")
        initial_count = len(response1.json()[activity]["participants"])
        
        # Unregister
        response2 = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response2.status_code == 200
        
        # Check updated participant count
        response3 = client.get("/activities")
        new_count = len(response3.json()[activity]["participants"])
        assert new_count == initial_count - 1
        assert email not in response3.json()[activity]["participants"]


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirect(self):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
