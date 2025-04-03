import pymongo
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from flask import Blueprint, request, jsonify, send_file
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
import pandas as pd
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('youtube_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

sentiment_bp = Blueprint('sentiment_bp', __name__)

# Download required NLTK data
try:
    nltk.download("vader_lexicon", quiet=True)
except Exception as e:
    logger.error(f"Error downloading NLTK data: {e}")

# Initialize Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

# Connect to MongoDB
try:
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["network"]
    collection = db["youtube"]
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Error connecting to MongoDB: {e}")
    collection = None

# Ensure "graphs" directory exists
if not os.path.exists("graphs"):
    os.makedirs("graphs")
    logger.info("Created graphs directory")

# YouTube API Configuration
API_KEY = os.getenv('YOUTUBE_API_KEY', 'YOUR_API_KEY_HERE')  # Get API key from environment variable
youtube = build("youtube", "v3", developerKey=API_KEY)

CATEGORY_MAPPING = {
    "1": "Film & Animation",
    "2": "Autos & Vehicles",
    "10": "Music",
    "15": "Pets & Animals",
    "17": "Sports",
    "18": "Short Movies",
    "19": "Travel & Events",
    "20": "Gaming",
    "21": "Videoblogging",
    "22": "People & Blogs",
    "23": "Comedy",
    "24": "Entertainment",
    "25": "News & Politics",
    "26": "Howto & Style",
    "27": "Education",
    "28": "Science & Technology",
    "29": "Nonprofits & Activism"
}

class YouTubeAnalyzer:
    def get_category_name(self, category_id):
        """Get category name using static mapping"""
        return CATEGORY_MAPPING.get(str(category_id), "Unknown")

    def parse_duration(self, duration):
        """Parse ISO 8601 duration to seconds"""
        try:
            hours = re.search(r'(\d+)H', duration)
            minutes = re.search(r'(\d+)M', duration)
            seconds = re.search(r'(\d+)S', duration)
            
            total_seconds = 0
            if hours:
                total_seconds += int(hours.group(1)) * 3600
            if minutes:
                total_seconds += int(minutes.group(1)) * 60
            if seconds:
                total_seconds += int(seconds.group(1))
            
            return total_seconds
        except Exception as e:
            logger.error(f"Error parsing duration: {e}")
            return 0

    def parse_date(self, date_str):
        """Parse date string to datetime object"""
        try:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        except Exception as e:
            logger.error(f"Error parsing date: {e}")
            return None

    def fetch_video_comments(self, video_id, max_comments=100):
        """Fetch video comments with pagination"""
        try:
            comments = []
            next_page_token = None

            while len(comments) < max_comments:
                request = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=100,
                    pageToken=next_page_token,
                    order="relevance"
                )
                response = request.execute()

                for item in response["items"]:
                    comment = item["snippet"]["topLevelComment"]["snippet"]
                    comments.append({
                        "comment": comment["textDisplay"],
                        "published_at": comment["publishedAt"],
                        "likes": comment.get("likeCount", 0)
                    })

                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    break

            return comments
        except HttpError as e:
            logger.error(f"Error fetching comments: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching comments: {e}")
            return []

    def search_channel(self, channel_name):
        """Search for a channel with improved error handling"""
        try:
            # First try exact search
            search_response = youtube.search().list(
                q=channel_name,
                type="channel",
                part="snippet",
                maxResults=5
            ).execute()

            if not search_response.get("items"):
                # Try with channel name variations
                variations = [
                    channel_name,
                    f"{channel_name} channel",
                    f"{channel_name} official",
                    f"{channel_name} youtube"
                ]
                
                for variation in variations:
                    search_response = youtube.search().list(
                        q=variation,
                        type="channel",
                        part="snippet",
                        maxResults=5
                    ).execute()
                    
                    if search_response.get("items"):
                        break

            if not search_response.get("items"):
                logger.warning(f"No channel found for: {channel_name}")
                return None

            # Find the best match
            best_match = None
            best_score = 0
            channel_name_lower = channel_name.lower()

            for item in search_response["items"]:
                title = item["snippet"]["title"].lower()
                description = item["snippet"].get("description", "").lower()
                
                # Calculate match score
                score = 0
                if channel_name_lower in title:
                    score += 2
                if channel_name_lower in description:
                    score += 1
                if item["snippet"].get("customUrl", "").lower() == channel_name_lower:
                    score += 3

                if score > best_score:
                    best_score = score
                    best_match = item

            if best_match:
                return best_match["id"]["channelId"]
            else:
                logger.warning(f"No good match found for channel: {channel_name}")
                return None

        except HttpError as e:
            logger.error(f"YouTube API Error during channel search: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during channel search: {e}")
            return None

    def fetch_channel_videos(self, channel_name, max_videos=10):
        """Fetch channel videos with pagination"""
        try:
            logger.info(f"Searching for channel: {channel_name}")
            channel_id = self.search_channel(channel_name)
            
            if not channel_id:
                logger.warning(f"Channel not found: {channel_name}")
                return None

            logger.info(f"Found channel ID: {channel_id}")

            channel_response = youtube.channels().list(
                part="contentDetails",
                id=channel_id
            ).execute()

            if not channel_response.get("items"):
                logger.warning(f"No channel details found for ID: {channel_id}")
                return None

            uploads_playlist = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

            playlist_items = []
            next_page_token = None

            while len(playlist_items) < max_videos:
                playlist_response = youtube.playlistItems().list(
                    playlistId=uploads_playlist,
                    part="snippet",
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()

                if not playlist_response.get("items"):
                    logger.warning("No videos found in playlist")
                    break

                playlist_items.extend(playlist_response["items"])
                next_page_token = playlist_response.get("nextPageToken")
                if not next_page_token:
                    break

            if not playlist_items:
                logger.warning("No videos found for channel")
                return None

            video_ids = [item["snippet"]["resourceId"]["videoId"] for item in playlist_items[:max_videos]]
            videos = []

            for i in range(0, len(video_ids), 50):
                batch = video_ids[i:i + 50]
                video_response = youtube.videos().list(
                    part="snippet,statistics,contentDetails",
                    id=",".join(batch)
                ).execute()

                for item in video_response["items"]:
                    try:
                        stats = item["statistics"]
                        video_id = item["id"]
                        duration = self.parse_duration(item["contentDetails"]["duration"])
                        comments = self.fetch_video_comments(video_id)
                        
                        videos.append({
                            "video_id": video_id,
                            "title": item["snippet"]["title"],
                            "description": item["snippet"].get("description", ""),
                            "category": self.get_category_name(item["snippet"]["categoryId"]),
                            "views": int(stats.get("viewCount", 0)),
                            "likes": int(stats.get("likeCount", 0)),
                            "comments": int(stats.get("commentCount", 0)),
                            "duration": duration,
                            "top_comments": comments,
                            "tags": item["snippet"].get("tags", []),
                            "published_at": item["snippet"]["publishedAt"]
                        })
                    except KeyError as e:
                        logger.warning(f"Missing video data: {e}")

            if not videos:
                logger.warning("No valid videos found after processing")
                return None

            return videos

        except HttpError as e:
            logger.error(f"YouTube API Error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

class NetworkAnalyzer:
    def analyze_network(self, videos):
        """Perform network analysis with centrality metrics"""
        try:
            G = nx.Graph()

            for video in videos:
                video_node = f"video_{video['video_id']}"
                category_node = f"category_{video['category']}"

                G.add_node(video_node, type="video", **video)
                G.add_node(category_node, type="category")

                engagement = video['likes'] + video['comments'] + (video['views'] / 1000)
                G.add_edge(video_node, category_node, weight=engagement * 0.5)

            descriptions = [video["description"] for video in videos]
            titles = [video["title"] for video in videos]

            vectorizer = TfidfVectorizer()
            tfidf_matrix_desc = vectorizer.fit_transform(descriptions)
            tfidf_matrix_title = vectorizer.fit_transform(titles)

            similarity_matrix_desc = cosine_similarity(tfidf_matrix_desc)
            similarity_matrix_title = cosine_similarity(tfidf_matrix_title)

            for i in range(len(videos)):
                for j in range(i + 1, len(videos)):
                    description_similarity = similarity_matrix_desc[i, j]
                    title_similarity = similarity_matrix_title[i, j]
                    combined_similarity = (description_similarity + title_similarity) / 2.0

                    if combined_similarity > 0.3:
                        G.add_edge(f"video_{videos[i]['video_id']}", f"video_{videos[j]['video_id']}", weight=combined_similarity)

            centrality = {
                "degree": nx.degree_centrality(G),
                "betweenness": nx.betweenness_centrality(G, weight='weight'),
                "closeness": nx.closeness_centrality(G)
            }
            try:
                centrality["eigenvector"] = nx.eigenvector_centrality(G, weight='weight', max_iter=2000)
            except nx.PowerIterationFailedConvergence:
                logger.warning("Eigenvector centrality did not converge.")
                centrality["eigenvector"] = {}
            return centrality
        except Exception as e:
            logger.error(f"NetworkX Error: {e}")
            return None

def extract_features(channel_data):
    """Extract features from video data for sentiment analysis & model training."""
    try:
        feature_list = []
        target = []
        engagement_metrics = {}
        video_sentiments = []
        hourly_sentiment = defaultdict(int)
        total_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}

        # Network Analysis
        net_analyzer = NetworkAnalyzer()
        videos = channel_data.get("videos", [])
        centrality = net_analyzer.analyze_network(videos)

        for video in videos:
            sentiments = {"Positive": 0, "Negative": 0, "Neutral": 0}
            comments = video.get("top_comments", [])

            if comments:  # Only process sentiments if there are comments
                for comment_data in comments:
                    comment_text = comment_data.get("comment", "")
                    score = sia.polarity_scores(comment_text)["compound"]

                    if score > 0.05:
                        sentiments["Positive"] += 1
                    elif score < -0.05:
                        sentiments["Negative"] += 1
                    else:
                        sentiments["Neutral"] += 1

                    published_at = comment_data.get("published_at", "")
                    if published_at:
                        try:
                            date = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
                            hour = date.hour
                            weekday = date.weekday()
                            hourly_sentiment[f"{weekday}-{hour}"] += 1
                        except (ValueError, IndexError) as e:
                            logger.warning(f"Error parsing date: {e}")

            # Add centrality metrics to video data
            video_node = f"video_{video.get('video_id', '')}"
            video_sentiments.append({
                "video_title": video.get("title", "Unknown Video"),
                **sentiments,
                "degree": centrality["degree"].get(video_node, 0) if centrality else 0,
                "betweenness": centrality["betweenness"].get(video_node, 0) if centrality else 0,
                "closeness": centrality["closeness"].get(video_node, 0) if centrality else 0,
                "eigenvector": centrality["eigenvector"].get(video_node, 0) if centrality and "eigenvector" in centrality else 0
            })

            for key in sentiments:
                total_counts[key] += sentiments[key]

            likes = video.get("likes", 0)
            views = video.get("views", 1)
            total_comments = len(comments)

            engagement_rate = (likes + total_comments) / views if views > 0 else 0
            view_to_like_ratio = likes / views if views > 0 else 0
            duration = video.get("duration", 10)
            tags = len(video.get("tags", []))

            video_features = {
                "positive_comments": sentiments["Positive"],
                "negative_comments": sentiments["Negative"],
                "neutral_comments": sentiments["Neutral"],
                "total_comments": total_comments,
                "likes": likes,
                "views": views,
                "engagement_rate": engagement_rate,
                "view_to_like_ratio": view_to_like_ratio,
                "duration": duration,
                "tags": tags,
                "degree_centrality": centrality["degree"].get(video_node, 0) if centrality else 0,
                "betweenness_centrality": centrality["betweenness"].get(video_node, 0) if centrality else 0,
                "closeness_centrality": centrality["closeness"].get(video_node, 0) if centrality else 0,
                "eigenvector_centrality": centrality["eigenvector"].get(video_node, 0) if centrality and "eigenvector" in centrality else 0
            }

            feature_list.append(video_features)
            target.append(views)

            engagement_metrics[video["title"]] = {
                "engagement_rate": round(engagement_rate, 3),
                "view_to_like_ratio": round(view_to_like_ratio, 3),
            }

        return (
            pd.DataFrame(feature_list),
            np.array(target),
            engagement_metrics,
            video_sentiments,
            hourly_sentiment,
            total_counts,
        )
    except Exception as e:
        logger.error(f"Error in extract_features: {e}")
        return None, None, None, None, None, None

def generate_sentiment_graph(sentiment_counts):
    """Generate and save sentiment analysis graph"""
    try:
        labels = list(sentiment_counts.keys())
        values = list(sentiment_counts.values())

        plt.figure(figsize=(6, 4))
        plt.bar(labels, values, color=['green', 'red', 'blue'])
        plt.xlabel("Sentiment")
        plt.ylabel("Count")
        plt.title("Sentiment Analysis of Comments")
        plt.savefig("graphs/sentiment.png")
        plt.close()
        logger.info("Successfully generated sentiment graph")
    except Exception as e:
        logger.error(f"Error in generating graph: {e}")

@sentiment_bp.route("/analyze_sentiment", methods=["GET"]) 
def analyze_sentiment():
    try:
        channel_name = request.args.get("channel")
        if not channel_name:
            logger.error("No channel name provided")
            return jsonify({"error": "Channel name is required"}), 400
        
        logger.info(f"Starting analysis for channel: {channel_name}")
        
        # Check API key
        if API_KEY == 'YOUR_API_KEY_HERE':
            logger.error("YouTube API key not configured")
            return jsonify({"error": "YouTube API key not configured. Please check your .env file."}), 500
        
        # Fetch channel data from YouTube API
        youtube_analyzer = YouTubeAnalyzer()
        videos = youtube_analyzer.fetch_channel_videos(channel_name)
        
        if not videos:
            logger.error(f"No videos found for channel: {channel_name}")
            return jsonify({"error": f"Channel '{channel_name}' not found or no videos available."}), 404

        logger.info(f"Found {len(videos)} videos for channel {channel_name}")

        # Create channel data structure
        channel_data = {
            "title": channel_name,
            "videos": videos
        }

        df_features, y, engagement_metrics, video_sentiments, hourly_sentiment, total_counts = extract_features(channel_data)

        if df_features is None or df_features.empty:
            logger.error("No sufficient data for predictions")
            return jsonify({"error": "No sufficient data for predictions."}), 400

        # Training and predicting using RandomForest
        X_train, X_test, y_train, y_test = train_test_split(df_features, y, test_size=0.2, random_state=42)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)

        predicted_views = model.predict(scaler.transform(df_features))
        predicted_performance = {
            video["title"]: int(pred) for video, pred in zip(videos, predicted_views)
        }

        best_time = max(hourly_sentiment, key=hourly_sentiment.get, default="Unknown")
        
        # Calculate total comments and sentiment percentages
        total_comments = sum(total_counts.values()) or 1
        sentiment_percentages = {
            key: round((count / total_comments) * 100, 2) for key, count in total_counts.items()
        }

        # Generate sentiment graph
        generate_sentiment_graph(total_counts)

        logger.info(f"Successfully completed analysis for channel: {channel_name}")
        
        # Return all required data
        return jsonify({
            "percentages": sentiment_percentages,
            "video_sentiments": video_sentiments,
            "hourly_sentiment": hourly_sentiment,
            "predicted_performance": predicted_performance,
            "best_time": f"{best_time}:00",
            "engagement_metrics": engagement_metrics,
            "sentiment_graph": "/sentiment/graph/sentiment"
        })

    except Exception as e:
        logger.error(f"Error in analyze_sentiment: {str(e)}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@sentiment_bp.route("/graph/sentiment", methods=["GET"])  
def get_sentiment_graph():
    try:
        return send_file("graphs/sentiment.png", mimetype="image/png")
    except Exception as e:
        logger.error(f"Error serving sentiment graph: {e}")
        return jsonify({"error": "Failed to serve sentiment graph"}), 500

@sentiment_bp.route("/search_channels", methods=["GET"])
def search_channels():
    try:
        query = request.args.get("query", "")
        if not query:
            logger.warning("Empty search query received")
            return jsonify({"channels": []})

        logger.info(f"Searching for channels with query: {query}")

        # Check API key
        if API_KEY == 'YOUR_API_KEY_HERE':
            logger.error("YouTube API key not configured")
            return jsonify({"error": "YouTube API key not configured. Please check your .env file."}), 500

        youtube_analyzer = YouTubeAnalyzer()
        
        # Try different search variations
        search_variations = [
            query,
            f"{query} channel",
            f"{query} official",
            f"{query} youtube"
        ]
        
        all_channels = []
        for variation in search_variations:
            try:
                logger.debug(f"Trying search variation: {variation}")
                search_response = youtube.search().list(
                    q=variation,
                    type="channel",
                    part="snippet",
                    maxResults=5
                ).execute()

                if search_response.get("items"):
                    for item in search_response["items"]:
                        # Check if this channel is already in our results
                        channel_id = item["id"]["channelId"]
                        if not any(ch["id"] == channel_id for ch in all_channels):
                            # Calculate match score
                            title = item["snippet"]["title"].lower()
                            description = item["snippet"].get("description", "").lower()
                            custom_url = item["snippet"].get("customUrl", "").lower()
                            query_lower = query.lower()
                            
                            score = 0
                            if query_lower in title:
                                score += 2
                            if query_lower in description:
                                score += 1
                            if custom_url == query_lower:
                                score += 3
                            
                            all_channels.append({
                                "id": channel_id,
                                "title": item["snippet"]["title"],
                                "description": item["snippet"].get("description", ""),
                                "thumbnail": item["snippet"]["thumbnails"]["default"]["url"],
                                "score": score
                            })
            except HttpError as e:
                logger.warning(f"Error searching with variation '{variation}': {e}")
                continue

        # Sort channels by score and take top 5
        channels = sorted(all_channels, key=lambda x: x["score"], reverse=True)[:5]
        
        # Remove score from final output
        for channel in channels:
            del channel["score"]

        if not channels:
            logger.warning(f"No channels found for query: {query}")
            return jsonify({"channels": [], "error": "No channels found. Try searching with the exact channel name or URL."})

        logger.info(f"Found {len(channels)} channels for query: {query}")
        return jsonify({"channels": channels})

    except HttpError as e:
        logger.error(f"YouTube API Error during channel search: {e}")
        return jsonify({"error": "Failed to search channels. Please check your API key and try again."}), 500
    except Exception as e:
        logger.error(f"Unexpected error during channel search: {str(e)}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500 