import time
import unittest
import requests
from tqdm import tqdm
from colorama import Fore, Style
from pymongo import MongoClient

# Flask API URL
API_URL = "http://127.0.0.1:5000"

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["network"]
collection = db["youtube"]

# Helper function to calculate engagement score
def calculate_score(likes, comments, views):
    if views == 0:
        return 0.0
    engagement = ((likes + comments) / views) * 100
    return round(min(engagement, 100), 2)

# Real Test Cases
class TestFlaskAPI(unittest.TestCase):
    def test_mongodb_connection(self):
        """Test MongoDB connection."""
        try:
            client.server_info()  # Check if MongoDB is reachable
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"MongoDB connection failed: {e}")

    def test_keyword_extraction(self):
        """Test keyword extraction."""
        from your_flask_app import extract_keywords  # Replace with your actual import
        text = "This is a test video about Python programming."
        keywords = extract_keywords(text)
        expected_keywords = ["test", "video", "python", "programming"]
        self.assertEqual(keywords, expected_keywords)

    def test_fetch_data_api(self):
        """Test /fetch API endpoint."""
        response = requests.post(f"{API_URL}/fetch", json={"channel_name": "test_channel"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("subscribers", data)
        self.assertIn("views", data)
        self.assertIn("total_videos", data)
        self.assertIn("keyword_analysis", data)
        self.assertIn("videos", data)

    def test_content_analysis_api(self):
        """Test /content_analysis API endpoint."""
        response = requests.post(f"{API_URL}/content_analysis", json={"channel_name": "test_channel"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("duration_analysis", data)
        self.assertIn("category_analysis", data)
        self.assertIn("interpretation", data)

    def test_error_handling_fetch_api(self):
        """Test error handling for /fetch API."""
        response = requests.post(f"{API_URL}/fetch", json={"channel_name": "invalid_channel"})
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())

    def test_error_handling_content_analysis_api(self):
        """Test error handling for /content_analysis API."""
        response = requests.post(f"{API_URL}/content_analysis", json={"channel_name": "invalid_channel"})
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())

    def test_empty_video_list(self):
        """Test empty video list handling."""
        from your_flask_app import analyze_keywords  # Replace with your actual import
        keywords = analyze_keywords([])
        self.assertEqual(keywords, [])

    def test_clustering(self):
        """Test K-Means clustering."""
        from your_flask_app import cluster_videos  # Replace with your actual import
        videos = [
            {"views": 1000, "likes": 100, "comments": 20},
            {"views": 5000, "likes": 500, "comments": 100},
            {"views": 100, "likes": 5, "comments": 1},
        ]
        clustered_videos = cluster_videos(videos)
        self.assertEqual(len(clustered_videos), 3)
        for video in clustered_videos:
            self.assertIn("cluster", video)

# Function to run all test cases with progress bar
def run_real_test_cases():
    test_cases = [
        ("Test Case 1: MongoDB Connection Test", "test_mongodb_connection"),
        ("Test Case 2: Keyword Extraction Test", "test_keyword_extraction"),
        ("Test Case 3: Fetch Data API Test", "test_fetch_data_api"),
        ("Test Case 4: Content Analysis API Test", "test_content_analysis_api"),
        ("Test Case 5: Error Handling Test for /fetch API", "test_error_handling_fetch_api"),
        ("Test Case 6: Error Handling Test for /content_analysis API", "test_error_handling_content_analysis_api"),
        ("Test Case 7: Empty Video List Test", "test_empty_video_list"),
        ("Test Case 8: Clustering Test", "test_clustering"),
    ]
    success_count = 0

    print(f"{Fore.YELLOW}Running {len(test_cases)} real test cases...{Style.RESET_ALL}\n")

    for name, test_method in tqdm(test_cases, desc="Testing", unit="test"):
        test_case = TestFlaskAPI(test_method)
        result = test_case.run()
        if result.wasSuccessful():
            success_count += 1
            print(f"{Fore.GREEN}{name}: Passed{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}{name}: Failed{Style.RESET_ALL}")

    print(f"\n{Fore.GREEN}All real test cases completed!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Success: {success_count}/{len(test_cases)}{Style.RESET_ALL}")
    if success_count == len(test_cases):
        print(f"{Fore.GREEN}Status: All tests passed!{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Status: Some tests failed.{Style.RESET_ALL}")

if __name__ == "__main__":
    run_real_test_cases()