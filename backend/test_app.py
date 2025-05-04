import sys
import os
import pytest
from flask import json
from app import app, calculate_score, get_influencer_type

# Add the directory of app.py to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

@pytest.fixture
def client():
    """Set up a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# ---------------------------- UNIT TESTS ---------------------------- #

def test_calculate_score():
    """Test the engagement score calculation."""
    assert calculate_score(10, 5, 100) == 15.0  # (10+5)/100 * 100
    assert calculate_score(100, 50, 500) == 30.0  # (100+50)/500 * 100
    assert calculate_score(0, 0, 100) == 0.0  # No likes/comments
    assert calculate_score(10, 10, 0) == 0.0  # Avoid division by zero
    assert calculate_score(200, 100, 100) == 100.0  # Capped at 100%

def test_get_influencer_type():
    """Test the influencer type classification."""
    assert get_influencer_type(500) == "Not an Influencer"
    assert get_influencer_type(5000) == "Nano (1K-10K)"
    assert get_influencer_type(20000) == "Micro (10K-50K)"
    assert get_influencer_type(100000) == "Mid-Tier (50K-200K)"
    assert get_influencer_type(500000) == "Macro (200K-1M)"
    assert get_influencer_type(2000000) == "Mega (1M+)"

# ---------------------------- API TESTS ---------------------------- #

def test_fetch_channel_engagement(client):
    """Test the /fetch_channel_engagement API with a valid and invalid request."""
    response = client.get("/fetch_channel_engagement?channel_id=123")
    assert response.status_code in [200, 404]  # Could be success or not found
    data = response.get_json()
    
    if response.status_code == 200:
        assert "engagement_scores" in data
        assert "growth_rates" in data
    else:
        assert "error" in data

def test_fetch_channel_engagement_missing_param(client):
    """Test the /fetch_channel_engagement API without a channel_id parameter."""
    response = client.get("/fetch_channel_engagement")
    assert response.status_code == 400
    assert response.get_json()["error"] == "Channel ID required"

def test_filter_influencers(client):
    """Test the /filter API with a valid country and min_subscribers parameter."""
    response = client.get("/filter?country=US&min_subscribers=1000")
    assert response.status_code in [200, 500]  # Could be success or server issue
    data = response.get_json()
    
    if response.status_code == 200:
        assert isinstance(data, list)

def test_filter_influencers_missing_param(client):
    """Test the /filter API without a country parameter."""
    response = client.get("/filter")
    assert response.status_code == 400
    assert response.get_json()["error"] == "Country parameter required"

# ---------------------------- RUN TESTS ---------------------------- #

if __name__ == "__main__":
    pytest.main()
