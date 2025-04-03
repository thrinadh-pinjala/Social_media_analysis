from flask import Blueprint, jsonify, request
from flask_cors import CORS
from googleapiclient.discovery import build
from wordcloud import WordCloud
import matplotlib
matplotlib.use("Agg")  # Use a non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
import traceback
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize YouTube API
YOUTUBE_API_KEY = "AIzaSyCrzhOfOwbaqTZZF6uTMWdN1VdE1p1R4pQ"
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Create blueprint
dash_bp = Blueprint('dashboard', __name__)
CORS(dash_bp)

@dash_bp.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def fetch_trending_videos(region_code="IN"):
    """Fetch real-time trending videos from YouTube"""
    try:
        request = youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode=region_code,
            maxResults=50
        )
        
        response = request.execute()
        
        if 'error' in response:
            logger.error(f"YouTube API Error: {response['error']}")
            return []
            
        items = response.get('items', [])
        if not items:
            logger.warning(f"No videos found for region: {region_code}")
            return []
            
        trending_videos = []
        for item in items:
            try:
                snippet = item.get('snippet', {})
                statistics = item.get('statistics', {})
                
                video_data = {
                    "title": snippet.get('title', ''),
                    "views": int(statistics.get('viewCount', 0)),
                    "likes": statistics.get('likeCount', 'N/A'),
                    "published_at": snippet.get('publishedAt', ''),
                    "channel_title": snippet.get('channelTitle', ''),
                    "thumbnail": snippet.get('thumbnails', {}).get('high', {}).get('url', '')
                }
                trending_videos.append(video_data)
                
            except Exception as e:
                logger.error(f"Error processing video: {str(e)}")
                continue
        
        # Sort by views
        trending_videos.sort(key=lambda x: x['views'], reverse=True)
        return trending_videos
        
    except Exception as e:
        logger.error(f"Error in fetch_trending_videos: {str(e)}")
        return []

@dash_bp.route('/get_trending_data')
def get_data():
    try:
        region = request.args.get('region', 'IN')
        videos = fetch_trending_videos(region)
        
        if not videos:
            return jsonify({
                "error": "No trending videos found",
                "details": "Unable to fetch trending videos. Please try again later.",
                "region": region
            }), 404
            
        return jsonify({
            'videos': videos,
            'region': region
        })
        
    except Exception as e:
        logger.error(f"Error in get_data: {str(e)}")
        return jsonify({
            "error": "Server error",
            "details": str(e),
            "region": region
        }), 500

@dash_bp.route('/wordcloud')
def get_wordcloud():
    try:
        region = request.args.get('region', 'IN')
        videos = fetch_trending_videos(region)
        
        if not videos:
            return jsonify({"error": "No trending videos found"}), 404
            
        # Combine all titles
        titles_text = " ".join(video['title'] for video in videos)
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            min_font_size=10,
            max_font_size=100
        ).generate(titles_text)
        
        # Convert to image
        plt.figure(figsize=(8, 4))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        
        # Save to buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='PNG', bbox_inches='tight', pad_inches=0)
        plt.close()
        img_buffer.seek(0)
        
        # Convert to base64
        img_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
        return jsonify({'wordcloud': f'data:image/png;base64,{img_str}'})
        
    except Exception as e:
        logger.error(f"Error generating wordcloud: {str(e)}")
        return jsonify({"error": str(e)}), 500

@dash_bp.route('/ping')
def ping():
    """Simple endpoint to check if the backend is running"""
    return jsonify({"status": "ok", "message": "Backend is running"}), 200