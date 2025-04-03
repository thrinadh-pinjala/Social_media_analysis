from flask import Flask, jsonify, request
from flask_cors import CORS
from googleapiclient.discovery import build
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize YouTube API
YOUTUBE_API_KEY = "AIzaSyAMQuiQgTerx8AnHxEWEmZ7pk27hpDj8uM"  # Using the same key as dash.py
logger.info("Initializing YouTube API with key: %s", YOUTUBE_API_KEY[:10] + "...")
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

@app.route('/test')
def test():
    return jsonify({"status": "ok"})

@app.route('/get_trending_data')  # Removed /dashboard prefix
def get_trending_data():
    try:
        region = request.args.get('region', 'IN')
        logger.info(f"Fetching trending videos for region: {region}")
        
        request = youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode=region,
            maxResults=10
        )
        logger.info("Executing YouTube API request...")
        response = request.execute()
        
        if 'error' in response:
            logger.error(f"API Error: {response['error']}")
            return jsonify({"error": response['error']}), 500
            
        videos = []
        for item in response.get("items", []):
            snippet = item.get("snippet", {})
            statistics = item.get("statistics", {})
            video_data = {
                "title": snippet.get("title", ""),
                "views": statistics.get("viewCount", "0"),
                "likes": statistics.get("likeCount", "N/A"),
                "published_at": snippet.get("publishedAt", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", "")
            }
            videos.append(video_data)
            
        logger.info(f"Successfully fetched {len(videos)} videos")
        return jsonify({"videos": videos, "region": region})
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting test server...")
    app.run(debug=True, port=5000) 