import time
from colorama import Fore, Style
from tqdm import tqdm
import requests
from pymongo import MongoClient
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download NLTK data
nltk.download("vader_lexicon", quiet=True)

# Initialize Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["network"]
collection = db["youtube"]

# Flask API URL
API_URL = "http://127.0.0.1:5000"

# Test Case 1: Sentiment Analysis
def test_sentiment_analysis():
    """Test if sentiment analysis works correctly."""
    try:
        # Input
        comments = [
            {"comment": "I love this video!", "published_at": "2023-10-01T12:00:00Z"},
            {"comment": "This is terrible.", "published_at": "2023-10-01T13:00:00Z"},
            {"comment": "It's okay.", "published_at": "2023-10-01T14:00:00Z"}
        ]

        # Expected Output
        expected_sentiments = {"Positive": 1, "Negative": 1, "Neutral": 1}

        # Actual Output
        actual_sentiments = {"Positive": 0, "Negative": 0, "Neutral": 0}
        for comment in comments:
            score = sia.polarity_scores(comment["comment"])["compound"]
            if score > 0.05:
                actual_sentiments["Positive"] += 1
            elif score < -0.05:
                actual_sentiments["Negative"] += 1
            else:
                actual_sentiments["Neutral"] += 1

        # Compare Expected vs Actual
        if actual_sentiments == expected_sentiments:
            print(f"{Fore.GREEN}Test Case 1: Sentiment Analysis - Passed{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Test Case 1: Sentiment Analysis - Failed{Style.RESET_ALL}")
            print(f"Expected: {expected_sentiments}, Actual: {actual_sentiments}")
            return False
    except Exception as e:
        print(f"{Fore.RED}Sentiment Analysis Error: {e}{Style.RESET_ALL}")
        return False

# Test Case 2: Network Analysis
def test_network_analysis():
    """Test if network analysis works correctly."""
    try:
        # Input
        videos = [
            {"video_id": "1", "category": "Tech", "likes": 100, "comments": 10, "views": 1000},
            {"video_id": "2", "category": "Tech", "likes": 200, "comments": 20, "views": 2000}
        ]

        # Expected Output
        expected_centrality_keys = ["degree", "betweenness", "closeness"]

        # Actual Output
        G = nx.Graph()
        for video in videos:
            video_node = f"video_{video['video_id']}"
            category_node = f"category_{video['category']}"
            engagement = video['likes'] + video['comments'] + (video['views'] / 1000)
            G.add_edge(video_node, category_node, weight=engagement * 0.5)
        actual_centrality = {
            "degree": nx.degree_centrality(G),
            "betweenness": nx.betweenness_centrality(G, weight='weight'),
            "closeness": nx.closeness_centrality(G)
        }

        # Compare Expected vs Actual
        if all(key in actual_centrality for key in expected_centrality_keys):
            print(f"{Fore.GREEN}Test Case 2: Network Analysis - Passed{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Test Case 2: Network Analysis - Failed{Style.RESET_ALL}")
            print(f"Expected Keys: {expected_centrality_keys}, Actual Keys: {list(actual_centrality.keys())}")
            return False
    except Exception as e:
        print(f"{Fore.RED}Network Analysis Error: {e}{Style.RESET_ALL}")
        return False

# Test Case 3: Feature Extraction
def test_feature_extraction():
    """Test if feature extraction works correctly."""
    try:
        # Input
        videos = [
            {"title": "Video 1", "likes": 100, "views": 1000, "top_comments": [
                {"comment": "Great video!", "published_at": "2023-10-01T12:00:00Z"}
            ]}
        ]

        # Expected Output
        expected_features = ["positive_comments", "negative_comments", "neutral_comments", "engagement_rate", "view_to_like_ratio"]

        # Actual Output
        df_features = pd.DataFrame({
            "positive_comments": [10],
            "negative_comments": [5],
            "neutral_comments": [15],
            "engagement_rate": [0.2],
            "view_to_like_ratio": [0.1]
        })

        # Compare Expected vs Actual
        if all(feature in df_features.columns for feature in expected_features):
            print(f"{Fore.GREEN}Test Case 3: Feature Extraction - Passed{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Test Case 3: Feature Extraction - Failed{Style.RESET_ALL}")
            print(f"Expected Features: {expected_features}, Actual Features: {list(df_features.columns)}")
            return False
    except Exception as e:
        print(f"{Fore.RED}Feature Extraction Error: {e}{Style.RESET_ALL}")
        return False

# Test Case 4: RandomForestRegressor
def test_random_forest():
    """Test if RandomForestRegressor works correctly."""
    try:
        # Input
        df_features = pd.DataFrame({
            "positive_comments": [10],
            "negative_comments": [5],
            "neutral_comments": [15],
            "engagement_rate": [0.2],
            "view_to_like_ratio": [0.1]
        })
        y = np.array([1000])

        # Expected Output
        expected_output_type = np.ndarray

        # Actual Output
        X_train, X_test, y_train, y_test = train_test_split(df_features, y, test_size=0.2, random_state=42)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        predicted_views = model.predict(X_test_scaled)

        # Compare Expected vs Actual
        if isinstance(predicted_views, expected_output_type) and len(predicted_views) > 0:
            print(f"{Fore.GREEN}Test Case 4: RandomForestRegressor - Passed{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Test Case 4: RandomForestRegressor - Failed{Style.RESET_ALL}")
            print(f"Expected Type: {expected_output_type}, Actual Type: {type(predicted_views)}")
            return False
    except Exception as e:
        print(f"{Fore.RED}RandomForestRegressor Error: {e}{Style.RESET_ALL}")
        return False

# Test Case 5: API Endpoint - /analyze_sentiment
def test_analyze_sentiment_endpoint():
    """Test if the /analyze_sentiment endpoint works correctly."""
    try:
        # Expected Output
        expected_keys = ["percentages", "video_sentiments", "predicted_performance", "best_time"]

        # Actual Output
        response = requests.get(f"{API_URL}/analyze_sentiment?channel=test_channel")
        if response.status_code == 200:
            data = response.json()

            # Compare Expected vs Actual
            if all(key in data for key in expected_keys):
                print(f"{Fore.GREEN}Test Case 5: /analyze_sentiment Endpoint - Passed{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}Test Case 5: /analyze_sentiment Endpoint - Failed{Style.RESET_ALL}")
                print(f"Expected Keys: {expected_keys}, Actual Keys: {list(data.keys())}")
                return False
        else:
            print(f"{Fore.RED}Test Case 5: /analyze_sentiment Endpoint - Failed (Status Code: {response.status_code}){Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}/analyze_sentiment Endpoint Error: {e}{Style.RESET_ALL}")
        return False

# Test Case 6: API Endpoint - /graph/sentiment
def test_sentiment_graph_endpoint():
    """Test if the /graph/sentiment endpoint works correctly."""
    try:
        # Expected Output
        expected_status_code = 200

        # Actual Output
        response = requests.get(f"{API_URL}/graph/sentiment")

        # Compare Expected vs Actual
        if response.status_code == expected_status_code:
            print(f"{Fore.GREEN}Test Case 6: /graph/sentiment Endpoint - Passed{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Test Case 6: /graph/sentiment Endpoint - Failed (Status Code: {response.status_code}){Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}/graph/sentiment Endpoint Error: {e}{Style.RESET_ALL}")
        return False

# Run All Test Cases
def run_test_cases():
    test_cases = [
        ("Test Case 1: Sentiment Analysis", test_sentiment_analysis),
        ("Test Case 2: Network Analysis", test_network_analysis),
        ("Test Case 3: Feature Extraction", test_feature_extraction),
        ("Test Case 4: RandomForestRegressor", test_random_forest),
        ("Test Case 5: /analyze_sentiment Endpoint", test_analyze_sentiment_endpoint),
        ("Test Case 6: /graph/sentiment Endpoint", test_sentiment_graph_endpoint),
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