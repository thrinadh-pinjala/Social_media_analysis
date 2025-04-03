from flask import Flask, request, jsonify
from flask_cors import CORS
import pymongo
import re
from collections import Counter, defaultdict
import nltk
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

# Download NLTK stopwords
nltk.download("stopwords")

app = Flask(__name__)
CORS(app)

# MongoDB Connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["network"]
collection = db["youtube"]

# Stopwords
STOPWORDS = set(nltk.corpus.stopwords.words("english"))

# 🔹 Category ID → Name Mapping
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

# 📌 Function to Extract Keywords
def extract_keywords(text):
    words = re.findall(r'\b\w+\b', text.lower())
    words = [word for word in words if word not in STOPWORDS and len(word) > 2]
    return words

# 📌 Function to Analyze Hashtags & Keywords
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

# 📌 K-Means Clustering for Video Performance
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

# 📌 Function: Categorize Videos by Duration
def categorize_duration(duration):
    if duration < 180:
        return "Short (<3 min)"
    elif duration < 600:
        return "Medium (3-10 min)"
    else:
        return "Long (>10 min)"

# 📌 Function: Analyze Content Type
def analyze_content_type(videos):
    duration_engagement = defaultdict(lambda: {"likes": 0, "views": 0, "count": 0})
    category_count = defaultdict(int)

    for video in videos:
        duration_category = categorize_duration(video.get("duration", 0))
        category_id = str(video.get("category_id", "Unknown"))  # Convert to string

        # Engagement Metrics
        views = video.get("views", 0)
        likes = video.get("likes", 0)

        # Update Duration Analysis
        duration_engagement[duration_category]["likes"] += likes
        duration_engagement[duration_category]["views"] += views
        duration_engagement[duration_category]["count"] += 1

        # Count Category Occurrences
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

    # Find Most Common Category ID
    most_common_category_id = max(category_count, key=category_count.get, default="Unknown")
    most_common_category_name = CATEGORY_MAPPING.get(most_common_category_id, "Unknown")

    interpretation = f"The channel mainly focuses on **{most_common_category_name}**."

    return {
        "duration_analysis": duration_analysis,
        "category_analysis": {CATEGORY_MAPPING.get(k, "Unknown"): v for k, v in category_count.items()},  # Map IDs to names
        "interpretation": interpretation
    }

# 📌 API to Fetch Data + Clustering
@app.route("/fetch", methods=["POST"])
def fetch_data():
    data = request.json
    channel_name = data.get("channel_name")

    channel_data = collection.find_one({"channel_name": channel_name})
    if not channel_data:
        return jsonify({"error": "Channel not found"}), 404

    videos = channel_data.get("videos", [])

    # Perform keyword analysis
    keyword_analysis = analyze_keywords(videos)

    # Perform clustering
    clustered_videos = cluster_videos(videos)

    return jsonify({
        "subscribers": channel_data.get("subscribers"),
        "views": channel_data.get("total_views"),
        "total_videos": channel_data.get("total_videos"),
        "keyword_analysis": keyword_analysis,
        "videos": clustered_videos
    })

# 📌 API: Fetch Content Type Analysis
@app.route("/content_analysis", methods=["POST"])
def fetch_content_analysis():
    data = request.json
    channel_name = data.get("channel_name")

    channel_data = collection.find_one({"channel_name": channel_name})
    if not channel_data:
        return jsonify({"error": "Channel not found"}), 404

    videos = channel_data.get("videos", [])
    content_analysis = analyze_content_type(videos)

    return jsonify(content_analysis)

if __name__ == "__main__":
    app.run(debug=True)
