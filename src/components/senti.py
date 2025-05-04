import pymongo
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
import pandas as pd
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Download VADER lexicon
nltk.download("vader_lexicon")

# Initialize Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["network"]
collection = db["youtube"]

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Ensure "graphs" directory exists
if not os.path.exists("graphs"):
    os.makedirs("graphs")

def extract_features(channel_data):
    """Extract features from video data for sentiment analysis & model training."""
    feature_list = []
    target = []
    engagement_metrics = {}
    video_sentiments = []
    hourly_sentiment = defaultdict(int)
    total_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}

    for video in channel_data.get("videos", []):
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

            # Extract comment hour from timestamp (YYYY-MM-DDTHH:MM:SSZ)
            published_at = comment_data.get("published_at", "")
            if published_at:
                hour = int(published_at[11:13])  # Extract hour (0-23)
                weekday = int(published_at[8:10]) % 7  # Map to 0-6 for days
                hourly_sentiment[f"{weekday}-{hour}"] += 1  # Format: "day-hour"

        video_sentiments.append({
            "video_title": video.get("title", "Unknown Video"),
            **sentiments
        })

        # Aggregate total sentiment counts
        for key in sentiments:
            total_counts[key] += sentiments[key]

        # Extract video features
        likes = video.get("likes", 0)
        views = video.get("views", 1)  # Avoid division by zero
        total_comments = len(comments)

        # Engagement metrics
        engagement_rate = (likes + total_comments) / views
        view_to_like_ratio = likes / views
        duration = video.get("duration", 10)  # Assume a default duration in minutes
        tags = len(video.get("tags", []))  # Count of tags

        video_features = {
            "positive_comments": sentiments["Positive"],
            "negative_comments": sentiments["Negative"],
            "neutral_comments": sentiments["Neutral"],
            "total_comments": total_comments,
            "likes": likes,
            "views": views,  # Target variable
            "engagement_rate": engagement_rate,
            "view_to_like_ratio": view_to_like_ratio,
            "duration": duration,
            "tags": tags
        }

        feature_list.append(video_features)
        target.append(views)  # Actual performance

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

@app.route("/analyze_sentiment", methods=["GET"])
def analyze_sentiment():
    """Fetch channel data, analyze sentiment, train model, and return insights."""
    channel_name = request.args.get("channel")

    # Fetch data from MongoDB
    channel_data = collection.find_one({"title": channel_name})
    if not channel_data:
        return jsonify({"error": f"Channel '{channel_name}' not found."}), 404

    (
        df_features,
        y,
        engagement_metrics,
        video_sentiments,
        hourly_sentiment,
        total_counts,
    ) = extract_features(channel_data)

    if df_features.empty:
        return jsonify({"error": "No sufficient data for predictions."}), 400

    # Prepare data for model
    X_train, X_test, y_train, y_test = train_test_split(df_features, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train Random Forest Model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)

    # Predict views for all videos
    predicted_views = model.predict(scaler.transform(df_features))
    predicted_performance = {
        video["title"]: int(pred) for video, pred in zip(channel_data.get("videos", []), predicted_views)
    }

    # Determine best posting time
    best_time = max(hourly_sentiment, key=hourly_sentiment.get, default="Unknown")

    # Compute sentiment percentages
    total_comments = sum(total_counts.values()) or 1  # Prevent division by zero
    sentiment_percentages = {
        key: round((count / total_comments) * 100, 2) for key, count in total_counts.items()
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
        "sentiment_graph": "/graph/sentiment"
    })

def generate_sentiment_graph(sentiment_counts):
    """Generate and save sentiment graph safely."""
    try:
        labels = list(sentiment_counts.keys())
        values = list(sentiment_counts.values())

        plt.figure(figsize=(6, 4))  # Create figure safely
        plt.bar(labels, values, color=['green', 'red', 'blue'])
        plt.xlabel("Sentiment")
        plt.ylabel("Count")
        plt.title("Sentiment Analysis of Comments")
        plt.savefig("graphs/sentiment.png")
        plt.close()  # Close the figure to free resources
    except Exception as e:
        print(f"Error in generating graph: {e}")

@app.route("/graph/sentiment", methods=["GET"])
def get_sentiment_graph():
    """Serve the sentiment graph."""
    return send_file("graphs/sentiment.png", mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True, threaded=True)  # Ensure Flask runs in a multi-threaded mode
