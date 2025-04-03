from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
CORS(app)

influencer_bp = Blueprint('influencer_bp', __name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["network"]
collection = db["youtube"]

CATEGORY_MAP = {
    "1": "Film & Animation",
    "2": "Autos & Vehicles",
    "10": "Music",
    "15": "Pets & Animals",
    "17": "Sports",
    "20": "Gaming",
    "22": "People & Blogs",
    "23": "Comedy",
    "24": "Entertainment",
    "25": "News & Politics",
    "26": "How-to & Style",
    "27": "Education",
    "28": "Science & Technology"
}

def calculate_score(likes, comments, views):
    if views == 0:
        return 0.0
    engagement = ((likes + comments) / views) * 100
    return round(min(engagement, 100), 2)

def get_influencer_type(subscriber_count):
    if subscriber_count < 1000:
        return "Not an Influencer"
    elif 1000 <= subscriber_count < 10000:
        return "Nano (1K-10K)"
    elif 10000 <= subscriber_count < 50000:
        return "Micro (10K-50K)"
    elif 50000 <= subscriber_count < 200000:
        return "Mid-Tier (50K-200K)"
    elif 200000 <= subscriber_count < 1000000:
        return "Macro (200K-1M)"
    return "Mega (1M+)"

@influencer_bp.route('/fetch_channel_engagement', methods=['GET'])
def fetch_channel_engagement():
    try:
        channel_id = request.args.get('channel_id')
        if not channel_id:
            return jsonify({"error": "Channel ID required"}), 400

        channel = collection.find_one({"channel_id": channel_id})
        if not channel:
            return jsonify({"error": "Channel not found"}), 404

        videos = channel.get("videos", [])
        category_engagement = defaultdict(float)
        for video in videos:
            category_id = str(video.get("category_id", "Unknown"))
            category_name = CATEGORY_MAP.get(category_id, f"Unknown ({category_id})")
            
            engagement = calculate_score(
                video.get("likes", 0),
                video.get("comments_count", 0),
                video.get("views", 1)
            )
            category_engagement[category_name] = min(
                category_engagement[category_name] + engagement,
                100.0
            )

        monthly_views = defaultdict(int)
        for video in videos:
            try:
                publish_date = datetime.strptime(video['published_at'], '%Y-%m-%dT%H:%M:%SZ')
                month_key = publish_date.strftime('%Y-%m')
                monthly_views[month_key] += video.get('views', 0)
            except Exception:
                continue

        sorted_months = sorted(monthly_views.items())
        growth_rates = {}
        prev_views = None
        
        for month, views in sorted_months:
            if prev_views and prev_views != 0:
                growth_rate = ((views - prev_views) / prev_views) * 100
                growth_rates[month] = round(growth_rate, 2)
            prev_views = views

        return jsonify({
            "engagement_scores": dict(category_engagement),
            "growth_rates": growth_rates
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@influencer_bp.route('/filter', methods=['GET'])
def filter_influencers():
    try:
        country = request.args.get('country')
        min_subscribers = request.args.get('min_subscribers', type=int, default=0)

        if not country:
            return jsonify({"error": "Country parameter required"}), 400

        query = {"country": country, "subscriber_count": {"$gte": min_subscribers}}
        influencers = list(collection.find(query))

        if not influencers:
            return jsonify({"message": "No influencers found."}), 404

        results = []
        for inf in influencers:
            subscriber_count = inf.get("subscriber_count", 0)
            total_likes = sum(v.get("likes", 0) for v in inf.get("videos", []))
            total_comments = sum(v.get("comments_count", 0) for v in inf.get("videos", []))

            engagement_rate = ((total_likes + total_comments) / subscriber_count * 100) if subscriber_count > 0 else 0

            results.append({
                "title": inf["title"],
                "channel_id": inf["channel_id"],
                "subscriber_count": subscriber_count,
                "engagement_rate": round(engagement_rate, 2),
                "influencer_type": get_influencer_type(subscriber_count)
            })

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

app.register_blueprint(influencer_bp)

if __name__ == '__main__':
    app.run(debug=True)
