import time
import requests
from tqdm import tqdm
from colorama import Fore, Style
from pymongo import MongoClient
import re
from collections import Counter, defaultdict
import nltk
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["network"]
collection = db["youtube"]

# Flask API URL
API_URL = "http://127.0.0.1:5000"

# Download NLTK stopwords
nltk.download("stopwords")
STOPWORDS = set(nltk.corpus.stopwords.words("english"))

# Helper function to calculate engagement score
def calculate_score(likes, comments, views):
    if views == 0:
        return 0.0
    engagement = ((likes + comments) / views) * 100
    return round(min(engagement, 100), 2)

# Function to extract keywords
def extract_keywords(text):
    words = re.findall(r'\b\w+\b', text.lower())
    words = [word for word in words if word not in STOPWORDS and len(word) > 2]
    return words

# Function to analyze keywords
def analyze_keywords(videos):
    keyword_count = Counter()
    for video in videos:
        tags = video.get("tags", [])
        if tags:
            keyword_count.update(tags)
        else:
            title_keywords = extract_keywords(video.get("title", ""))
            desc_keywords = extract_keywords(video.get("description", ""))
            keyword_count.update(title_keywords + desc_keywords)
    top_keywords = keyword_count.most_common(20)
    return [{"keyword": word, "count": count} for word, count in top_keywords]

# Function to cluster videos using K-Means
def cluster_videos(videos):
    if not videos:
        return []

    # Extract numerical features
    data = []
    for video in videos:
        views = video.get("views", 0)
        likes = video.get("likes", 0)
        comments = video.get("comments", 0)
        data.append([views, likes, comments])

    # Convert to numpy array
    data = np.array(data)

    # Normalize data
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data)

    # Apply K-Means
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(scaled_data)

    # Assign cluster labels
    for i, video in enumerate(videos):
        cluster_label = clusters[i]
        if cluster_label == 0:
            video["cluster"] = "Low Engagement"
        elif cluster_label == 1:
            video["cluster"] = "Medium Engagement"
        else:
            video["cluster"] = "High Engagement"

    return videos

# Function to categorize video duration
def categorize_duration(duration):
    if duration < 180:
        return "Short (<3 min)"
    elif duration < 600:
        return "Medium (3-10 min)"
    else:
        return "Long (>10 min)"

# Function to analyze content type
def analyze_content_type(videos):
    duration_engagement = defaultdict(lambda: {"likes": 0, "views": 0, "count": 0})
    category_count = defaultdict(int)

    for video in videos:
        duration_category = categorize_duration(video.get("duration", 0))
        category_id = str(video.get("category_id", "Unknown"))

        # Engagement metrics
        views = video.get("views", 0)
        likes = video.get("likes", 0)

        # Update duration analysis
        duration_engagement[duration_category]["likes"] += likes
        duration_engagement[duration_category]["views"] += views
        duration_engagement[duration_category]["count"] += 1

        # Count category occurrences
        category_count[category_id] += 1

    # Convert to JSON-friendly format
    duration_analysis = [
        {
            "duration": key,
            "avg_likes": value["likes"] / max(value["count"], 1),
            "avg_views": value["views"] / max(value["count"], 1)
        }
        for key, value in duration_engagement.items()
    ]

    # Find most common category ID
    most_common_category_id = max(category_count, key=category_count.get, default="Unknown")
    most_common_category_name = CATEGORY_MAPPING.get(most_common_category_id, "Unknown")

    interpretation = f"The channel mainly focuses on *{most_common_category_name}*."

    return {
        "duration_analysis": duration_analysis,
        "category_analysis": {CATEGORY_MAPPING.get(k, "Unknown"): v for k, v in category_count.items()},
        "interpretation": interpretation
    }

# Real test cases
def test_case_1():
    """Test if the MongoDB connection is successful."""
    try:
        # Expected Output: MongoDB connection should be successful
        client.server_info()  # Check if MongoDB is reachable
        print(f"{Fore.GREEN}Test Case 1: MongoDB Connection - Passed{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}Test Case 1: MongoDB Connection - Failed{Style.RESET_ALL}")
        print(f"Error: {e}")
        return False

def test_case_2():
    """Test if the keyword extraction works correctly."""
    try:
        # Input
        text = "This is a test video about Python programming and data analysis."
        
        # Expected Output
        expected_keywords = ["test", "video", "python", "programming", "data", "analysis"]
        
        # Actual Output
        extracted_keywords = extract_keywords(text)
        
        # Compare Expected vs Actual
        if set(extracted_keywords) == set(expected_keywords):
            print(f"{Fore.GREEN}Test Case 2: Keyword Extraction - Passed{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Test Case 2: Keyword Extraction - Failed{Style.RESET_ALL}")
            print(f"Expected: {expected_keywords}, Actual: {extracted_keywords}")
            return False
    except Exception as e:
        print(f"{Fore.RED}Test Case 2: Keyword Extraction - Failed{Style.RESET_ALL}")
        print(f"Error: {e}")
        return False

def test_case_3():
    """Test if the keyword analysis works correctly."""
    try:
        # Input
        videos = [
            {"title": "Python Tutorial", "description": "Learn Python programming", "tags": ["python", "tutorial"]},
            {"title": "Data Analysis", "description": "Analyze data with Python", "tags": ["data", "analysis"]}
        ]
        
        # Expected Output: A list of keywords with counts
        expected_output_type = list
        
        # Actual Output
        keyword_analysis = analyze_keywords(videos)
        
        # Compare Expected vs Actual
        if isinstance(keyword_analysis, expected_output_type) and len(keyword_analysis) > 0:
            print(f"{Fore.GREEN}Test Case 3: Keyword Analysis - Passed{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Test Case 3: Keyword Analysis - Failed{Style.RESET_ALL}")
            print(f"Expected Type: {expected_output_type}, Actual Type: {type(keyword_analysis)}")
            return False
    except Exception as e:
        print(f"{Fore.RED}Test Case 3: Keyword Analysis - Failed{Style.RESET_ALL}")
        print(f"Error: {e}")
        return False

def test_case_4():
    """Test if the K-Means clustering works correctly."""
    try:
        # Input
        videos = [
            {"views": 1000, "likes": 100, "comments": 20},
            {"views": 5000, "likes": 500, "comments": 100},
            {"views": 10000, "likes": 1000, "comments": 200}
        ]
        
        # Expected Output: A list of videos with cluster labels
        expected_output_type = list
        
        # Actual Output
        clustered_videos = cluster_videos(videos)
        
        # Compare Expected vs Actual
        if isinstance(clustered_videos, expected_output_type) and len(clustered_videos) > 0:
            print(f"{Fore.GREEN}Test Case 4: K-Means Clustering - Passed{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Test Case 4: K-Means Clustering - Failed{Style.RESET_ALL}")
            print(f"Expected Type: {expected_output_type}, Actual Type: {type(clustered_videos)}")
            return False
    except Exception as e:
        print(f"{Fore.RED}Test Case 4: K-Means Clustering - Failed{Style.RESET_ALL}")
        print(f"Error: {e}")
        return False

def test_case_5():
    """Test if the duration categorization works correctly."""
    try:
        # Input
        durations = [60, 300, 1200]
        
        # Expected Output
        expected_categories = ["Short (<3 min)", "Medium (3-10 min)", "Long (>10 min)"]
        
        # Actual Output
        results = [categorize_duration(duration) for duration in durations]
        
        # Compare Expected vs Actual
        if results == expected_categories:
            print(f"{Fore.GREEN}Test Case 5: Duration Categorization - Passed{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Test Case 5: Duration Categorization - Failed{Style.RESET_ALL}")
            print(f"Expected: {expected_categories}, Actual: {results}")
            return False
    except Exception as e:
        print(f"{Fore.RED}Test Case 5: Duration Categorization - Failed{Style.RESET_ALL}")
        print(f"Error: {e}")
        return False

def test_case_6():
    """Test if the content type analysis works correctly."""
    try:
        # Input
        videos = [
            {"duration": 60, "category_id": "1", "views": 1000, "likes": 100},
            {"duration": 300, "category_id": "2", "views": 5000, "likes": 500},
            {"duration": 1200, "category_id": "1", "views": 10000, "likes": 1000}
        ]
        
        # Expected Output: A dictionary with duration and category analysis
        expected_output_type = dict
        
        # Actual Output
        content_analysis = analyze_content_type(videos)
        
        # Compare Expected vs Actual
        if isinstance(content_analysis, expected_output_type) and "duration_analysis" in content_analysis:
            print(f"{Fore.GREEN}Test Case 6: Content Type Analysis - Passed{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Test Case 6: Content Type Analysis - Failed{Style.RESET_ALL}")
            print(f"Expected Type: {expected_output_type}, Actual Type: {type(content_analysis)}")
            return False
    except Exception as e:
        print(f"{Fore.RED}Test Case 6: Content Type Analysis - Failed{Style.RESET_ALL}")
        print(f"Error: {e}")
        return False

def test_case_7():
    """Test if the /fetch endpoint returns the expected response structure."""
    try:
        # Expected Output: A dictionary with specific keys
        expected_keys = ["subscribers", "views", "total_videos", "keyword_analysis", "videos"]
        
        # Actual Output
        response = requests.post(f"{API_URL}/fetch", json={"channel_name": "test_channel"})
        if response.status_code == 200:
            data = response.json()
            
            # Compare Expected vs Actual
            if all(key in data for key in expected_keys):
                print(f"{Fore.GREEN}Test Case 7: /fetch Endpoint - Passed{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}Test Case 7: /fetch Endpoint - Failed{Style.RESET_ALL}")
                print(f"Expected Keys: {expected_keys}, Actual Keys: {list(data.keys())}")
                return False
        else:
            print(f"{Fore.RED}Test Case 7: /fetch Endpoint - Failed (Status Code: {response.status_code}){Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}Test Case 7: /fetch Endpoint - Failed{Style.RESET_ALL}")
        print(f"Error: {e}")
        return False

def test_case_8():
    """Test if the /content_analysis endpoint returns the expected response structure."""
    try:
        # Expected Output: A dictionary with specific keys
        expected_keys = ["duration_analysis", "category_analysis", "interpretation"]
        
        # Actual Output
        response = requests.post(f"{API_URL}/content_analysis", json={"channel_name": "test_channel"})
        if response.status_code == 200:
            data = response.json()
            
            # Compare Expected vs Actual
            if all(key in data for key in expected_keys):
                print(f"{Fore.GREEN}Test Case 8: /content_analysis Endpoint - Passed{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}Test Case 8: /content_analysis Endpoint - Failed{Style.RESET_ALL}")
                print(f"Expected Keys: {expected_keys}, Actual Keys: {list(data.keys())}")
                return False
        else:
            print(f"{Fore.RED}Test Case 8: /content_analysis Endpoint - Failed (Status Code: {response.status_code}){Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}Test Case 8: /content_analysis Endpoint - Failed{Style.RESET_ALL}")
        print(f"Error: {e}")
        return False

def test_case_9():
    """Test if the API returns a 404 error when the channel is not found."""
    try:
        # Expected Output: Status code 404
        expected_status_code = 404
        
        # Actual Output
        response = requests.post(f"{API_URL}/fetch", json={"channel_name": "non_existent_channel"})
        
        # Compare Expected vs Actual
        if response.status_code == expected_status_code:
            print(f"{Fore.GREEN}Test Case 9: Channel Not Found - Passed{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Test Case 9: Channel Not Found - Failed{Style.RESET_ALL}")
            print(f"Expected Status Code: {expected_status_code}, Actual Status Code: {response.status_code}")
            return False
    except Exception as e:
        print(f"{Fore.RED}Test Case 9: Channel Not Found - Failed{Style.RESET_ALL}")
        print(f"Error: {e}")
        return False

def test_case_10():
    """Test if the stopwords are filtered correctly."""
    try:
        # Input
        text = "This is a test video about Python programming and data analysis."
        
        # Expected Output: Keywords without stopwords
        expected_keywords = ["test", "video", "python", "programming", "data", "analysis"]
        
        # Actual Output
        extracted_keywords = extract_keywords(text)
        
        # Compare Expected vs Actual
        if set(extracted_keywords) == set(expected_keywords):
            print(f"{Fore.GREEN}Test Case 10: Stopwords Filtering - Passed{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Test Case 10: Stopwords Filtering - Failed{Style.RESET_ALL}")
            print(f"Expected: {expected_keywords}, Actual: {extracted_keywords}")
            return False
    except Exception as e:
        print(f"{Fore.RED}Test Case 10: Stopwords Filtering - Failed{Style.RESET_ALL}")
        print(f"Error: {e}")
        return False

def test_case_11():
    """Test if the engagement score calculation is correct."""
    try:
        # Input
        likes, comments, views = 100, 20, 1000
        
        # Expected Output
        expected_score = calculate_score(likes, comments, views)
        
        # Actual Output
        actual_score = ((likes + comments) / views) * 100
        
        # Compare Expected vs Actual
        if round(actual_score, 2) == expected_score:
            print(f"{Fore.GREEN}Test Case 11: Engagement Score Calculation - Passed{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Test Case 11: Engagement Score Calculation - Failed{Style.RESET_ALL}")
            print(f"Expected: {expected_score}, Actual: {round(actual_score, 2)}")
            return False
    except Exception as e:
        print(f"{Fore.RED}Test Case 11: Engagement Score Calculation - Failed{Style.RESET_ALL}")
        print(f"Error: {e}")
        return False

# Function to run all test cases
def run_test_cases():
    test_cases = [
        ("Test Case 1: MongoDB Connection Test", test_case_1),
        ("Test Case 2: Keyword Extraction Test", test_case_2),
        ("Test Case 3: Keyword Analysis Test", test_case_3),
        ("Test Case 4: K-Means Clustering Test", test_case_4),
        ("Test Case 5: Duration Categorization Test", test_case_5),
        ("Test Case 6: Content Type Analysis Test", test_case_6),
        ("Test Case 7: Fetch Data API Test", test_case_7),
        ("Test Case 8: Content Analysis API Test", test_case_8),
        ("Test Case 9: Channel Not Found Test", test_case_9),
        ("Test Case 10: Stopwords Filtering Test", test_case_10),
        ("Test Case 11: Engagement Score Calculation Test", test_case_11),
    ]
    success_count = 0

    print(f"{Fore.YELLOW}Running {len(test_cases)} test cases...{Style.RESET_ALL}\n")

    for name, test_case in tqdm(test_cases, desc="Testing", unit="test"):
        if test_case():
            success_count += 1

    print(f"\n{Fore.GREEN}All test cases completed!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Success: {success_count}/{len(test_cases)}{Style.RESET_ALL}")
    if success_count == len(test_cases):
        print(f"{Fore.GREEN}Status: All tests passed!{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Status: Some tests failed.{Style.RESET_ALL}")

if __name__ == "__main__":
    run_test_cases()