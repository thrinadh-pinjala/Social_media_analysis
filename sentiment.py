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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sentiment_bp = Blueprint('sentiment_bp', __name__)

# Download VADER lexicon
try:
    nltk.download("vader_lexicon", quiet=True)
except Exception as e:
    logger.error(f"Error downloading VADER lexicon: {e}")

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

class NetworkAnalyzer:
    def analyze_network(self, videos):
        """Perform network analysis with centrality metrics"""
        if not videos:
            return None
            
        G = nx.Graph()
        
        try:
            for video in videos:
                video_node = f"video_{video.get('video_id', '')}"
                category_node = f"category_{video.get('category', '')}"
                
                G.add_node(video_node, type="video", **video)
                G.add_node(category_node, type="category")
                
                engagement = video.get('likes', 0) + video.get('comments', 0) + (video.get('views', 0) / 1000)
                G.add_edge(video_node, category_node, weight=engagement * 0.5)
            
            descriptions = [video.get("description", "") for video in videos]
            titles = [video.get("title", "") for video in videos]
            
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
                        G.add_edge(
                            f"video_{videos[i].get('video_id', '')}", 
                            f"video_{videos[j].get('video_id', '')}", 
                            weight=combined_similarity
                        )
            
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
    if not channel_data or not channel_data.get("videos"):
        return None, None, None, None, None, None
        
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
                    hour = int(published_at[11:13])
                    weekday = int(published_at[8:10]) % 7
                    hourly_sentiment[f"{weekday}-{hour}"] += 1
                except (ValueError, IndexError):
                    continue
        
        # Add centrality metrics to video data
        video_node = f"video_{video.get('video_id', '')}"
        video_sentiments.append({
            "video_title": video.get("title", "Unknown Video"),
            **sentiments,
            "degree": round(centrality["degree"].get(video_node, 0), 4) if centrality else 0,
            "betweenness": round(centrality["betweenness"].get(video_node, 0), 4) if centrality else 0,
            "closeness": round(centrality["closeness"].get(video_node, 0), 4) if centrality else 0,
            "eigenvector": round(centrality["eigenvector"].get(video_node, 0), 4) if centrality and "eigenvector" in centrality else 0
        })
        
        for key in sentiments:
            total_counts[key] += sentiments[key]
        
        likes = video.get("likes", 0)
        views = video.get("views", 1)
        total_comments = len(comments)
        
        engagement_rate = (likes + total_comments) / views
        view_to_like_ratio = likes / views
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
            "tags": tags
        }
        
        feature_list.append(video_features)
        target.append(views)
        
        engagement_metrics[video.get("title", "Unknown Video")] = {
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

@sentiment_bp.route("/analyze_sentiment", methods=["GET"])
def analyze_sentiment():
    try:
        channel_name = request.args.get("channel")
        if not channel_name:
            return jsonify({"error": "Channel name is required"}), 400
            
        # Retrieve channel data from MongoDB
        channel_data = collection.find_one({"title": channel_name})
        if not channel_data:
            return jsonify({"error": f"Channel '{channel_name}' not found"}), 404
            
        df_features, y, engagement_metrics, video_sentiments, hourly_sentiment, total_counts = extract_features(channel_data)
        
        if df_features.empty:
            return jsonify({"error": "No sufficient data for predictions"}), 400
            
        # Training and predicting using RandomForest
        X_train, X_test, y_train, y_test = train_test_split(df_features, y, test_size=0.2, random_state=42)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        predicted_views = model.predict(scaler.transform(df_features))
        predicted_performance = {
            video.get("title", "Unknown Video"): int(pred) 
            for video, pred in zip(channel_data.get("videos", []), predicted_views)
        }
        
        best_time = max(hourly_sentiment.items(), key=lambda x: x[1], default=("Unknown", 0))[0]
        
        # Calculate total comments and sentiment percentages
        total_comments = sum(total_counts.values()) or 1
        sentiment_percentages = {
            key: round((count / total_comments) * 100, 2) 
            for key, count in total_counts.items()
        }
        
        # Generate sentiment graph
        generate_sentiment_graph(total_counts)
        
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
        logger.error(f"Error in analyze_sentiment: {e}")
        return jsonify({"error": "Internal server error"}), 500

def generate_sentiment_graph(sentiment_counts):
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
    except Exception as e:
        logger.error(f"Error generating sentiment graph: {e}")

@sentiment_bp.route("/graph/sentiment", methods=["GET"])
def get_sentiment_graph():
    try:
        return send_file("graphs/sentiment.png", mimetype="image/png")
    except Exception as e:
        logger.error(f"Error serving sentiment graph: {e}")
        return jsonify({"error": "Graph not found"}), 404 