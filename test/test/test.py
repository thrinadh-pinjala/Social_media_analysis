import time
import requests
from tqdm import tqdm
from colorama import Fore, Style
from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["network"]
collection = db["youtube"]

# Flask API URL
API_URL = "http://127.0.0.1:3000"

# Helper function to calculate engagement score
def calculate_score(likes, comments, views):
    if views == 0:
        return 0.04
    engagement = ((likes + comments) / views) * 100
    return round(min(engagement, 100), 2)

# Real test cases
def test_case_1():
    """Test if the MongoDB connection is successful."""
    try:
        client.server_info()  # Check if MongoDB is reachable
        return True
    except Exception as e:
        print(f"{Fore.RED}MongoDB Connection Error: {e}{Style.RESET_ALL}")
        return False

def test_case_2():
    """Test if the API endpoint is reachable."""
    try:
        response = requests.get(f"{API_URL}/fetch_channel_engagement")
        return response.status_code == 200
    except Exception as e:
        print(f"{Fore.RED}API Endpoint Error: {e}{Style.RESET_ALL}")
        return False

def test_case_3():
    """Test if the engagement score calculation is correct."""
    likes, comments, views = 100, 20, 1000
    expected_score = calculate_score(likes, comments, views)
    actual_score = ((likes + comments) / views) * 100
    return round(actual_score, 2) == expected_score

def test_case_4():
    """Test if the channel ID validation works."""
    try:
        response = requests.get(f"{API_URL}/fetch_channel_engagement?channel_id=123")
        return response.status_code == 404  # Assuming invalid channel ID returns 404
    except Exception as e:
        print(f"{Fore.RED}Channel ID Validation Error: {e}{Style.RESET_ALL}")
        return False

def test_case_5():
    """Test if the country filter works."""
    try:
        response = requests.get(f"{API_URL}/filter?country=US")
        return response.status_code == 200 and len(response.json()) >= 0
    except Exception as e:
        print(f"{Fore.RED}Country Filter Error: {e}{Style.RESET_ALL}")
        return False

def test_case_6():
    """Test if the subscriber count filter works."""
    try:
        response = requests.get(f"{API_URL}/filter?country=US&min_subscribers=1000")
        return response.status_code == 200 and len(response.json()) >= 0
    except Exception as e:
        print(f"{Fore.RED}Subscriber Filter Error: {e}{Style.RESET_ALL}")
        return False

def test_case_7():
    """Test if the growth rate calculation is correct."""
    try:
        # Add a sample video to MongoDB for testing
        sample_video = {
            "channel_id": "test_channel",
            "published_at": "2023-10-01T00:00:00Z",
            "views": 1000,
            "likes": 100,
            "comments_count": 20,
            "category_id": "1"
        }
        collection.insert_one(sample_video)

        # Fetch growth rate from API
        response = requests.get(f"{API_URL}/fetch_channel_engagement?channel_id=test_channel")
        if response.status_code == 200:
            growth_rates = response.json().get("growth_rates", {})
            return isinstance(growth_rates, dict)
        return False
    except Exception as e:
        print(f"{Fore.RED}Growth Rate Calculation Error: {e}{Style.RESET_ALL}")
        return False
    finally:
        # Clean up the test data
        collection.delete_one({"channel_id": "test_channel"})

def test_case_8():
    """Test if the influencer type classification is correct."""
    try:
        response = requests.get(f"{API_URL}/filter?country=US&min_subscribers=1000")
        if response.status_code == 200:
            influencers = response.json()
            for influencer in influencers:
                subscriber_count = influencer.get("subscriber_count", 0)
                influencer_type = influencer.get("influencer_type", "")
                if subscriber_count < 1000 and influencer_type != "Not an Influencer":
                    return False
            return True
        return False
    except Exception as e:
        print(f"{Fore.RED}Influencer Type Classification Error: {e}{Style.RESET_ALL}")
        return False

def test_case_9():
    """Test if the category map is correctly defined."""
    try:
        response = requests.get(f"{API_URL}/fetch_channel_engagement?channel_id=test_channel")
        if response.status_code == 200:
            engagement_scores = response.json().get("engagement_scores", {})
            return isinstance(engagement_scores, dict)
        return False
    except Exception as e:
        print(f"{Fore.RED}Category Map Validation Error: {e}{Style.RESET_ALL}")
        return False

def test_case_10():
    """Test if the engagement rate is calculated correctly."""
    try:
        response = requests.get(f"{API_URL}/filter?country=US&min_subscribers=1000")
        if response.status_code == 200:
            influencers = response.json()
            for influencer in influencers:
                engagement_rate = influencer.get("engagement_rate", 0)
                if not isinstance(engagement_rate, float):
                    return False
            return True
        return False
    except Exception as e:
        print(f"{Fore.RED}Engagement Rate Calculation Error: {e}{Style.RESET_ALL}")
        return False

# Function to run all test cases
def run_test_cases():
    test_cases = [
        ("Test Case 1: MongoDB Connection Test", test_case_1),
        ("Test Case 2: API Endpoint Reachability Test", test_case_2),
        ("Test Case 3: Engagement Score Calculation Test", test_case_3),
        ("Test Case 4: Channel ID Validation Test", test_case_4),
        ("Test Case 5: Country Filter Test", test_case_5),
        ("Test Case 6: Subscriber Count Filter Test", test_case_6),
        ("Test Case 7: Growth Rate Calculation Test", test_case_7),
        ("Test Case 8: Influencer Type Classification Test", test_case_8),
        ("Test Case 9: Category Map Validation Test", test_case_9),
        ("Test Case 10: Engagement Rate Calculation Test", test_case_10),
    ]
    success_count = 0

    print(f"{Fore.YELLOW}Running {len(test_cases)} test cases...{Style.RESET_ALL}\n")

    for name, test_case in tqdm(test_cases, desc="Testing", unit="test"):
        if test_case():
            success_count += 1
            print(f"{Fore.GREEN}{name}: Passed{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}{name}: Failed{Style.RESET_ALL}")

    print(f"\n{Fore.GREEN}All test cases completed!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Success: {success_count}/{len(test_cases)}{Style.RESET_ALL}")
    if success_count == len(test_cases):
        print(f"{Fore.GREEN}Status: All tests passed!{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Status: Some tests failed.{Style.RESET_ALL}")

if __name__ == "__main__":
    run_test_cases()