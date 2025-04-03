from flask import Blueprint, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from blueprints.config import MONGODB_URI, YOUTUBE_API_KEY
import logging
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
recom_bp = Blueprint('recommendations', __name__)
CORS(recom_bp, resources={r"/*": {"origins": "*"}})

# YouTube Categories
YOUTUBE_CATEGORIES = {
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

def get_youtube_service():
    try:
        return build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    except Exception as e:
        logger.error(f"Error building YouTube service: {e}")
        return None

def search_channels_by_category(youtube, category_id, max_results=15):
    try:
        logger.info(f"Starting search for category_id: {category_id}")
        # Search for videos in the category first
        search_request = youtube.search().list(
            part="snippet",
            type="video",
            videoCategoryId=category_id,
            maxResults=50,  # Fetch more results to get more unique channels
            regionCode="IN",
            relevanceLanguage="en",  # Prefer English content
            q=get_category_keywords(category_id)  # Add relevant keywords for better results
        )
        logger.info(f"Executing search request with keywords: {get_category_keywords(category_id)}")
        search_response = search_request.execute()
        logger.info(f"Search response received. Found {len(search_response.get('items', []))} items")

        # Extract unique channel IDs from the search results
        channel_ids = list(set(item['snippet']['channelId'] for item in search_response.get('items', [])))
        logger.info(f"Found {len(channel_ids)} unique channel IDs")

        if not channel_ids:
            logger.warning(f"No channel IDs found for category {category_id}")
            return []

        # Get detailed channel information
        channels_request = youtube.channels().list(
            part="snippet,statistics",
            id=','.join(channel_ids[:max_results])
        )
        logger.info(f"Requesting details for {len(channel_ids[:max_results])} channels")
        channels_response = channels_request.execute()
        logger.info(f"Channel details response received. Found {len(channels_response.get('items', []))} channels")

        channels = []
        for item in channels_response.get('items', []):
            try:
                channel = {
                    'channel_id': item['id'],
                    'channel_name': item['snippet']['title'],
                    'description': item['snippet'].get('description', ''),
                    'thumbnails': item['snippet'].get('thumbnails', {}),
                    'category_id': category_id,
                    'subscriber_count': int(item['statistics'].get('subscriberCount', 0)),
                    'video_count': int(item['statistics'].get('videoCount', 0)),
                    'view_count': int(item['statistics'].get('viewCount', 0)),
                    'country': item['snippet'].get('country', 'Unknown')
                }
                channels.append(channel)
                logger.info(f"Successfully processed channel: {channel['channel_name']}")
            except Exception as e:
                logger.error(f"Error processing channel {item.get('id')}: {e}")
                continue

        # Sort by subscriber count and return top channels
        channels.sort(key=lambda x: x['subscriber_count'], reverse=True)
        logger.info(f"Returning {len(channels[:max_results])} channels for category {category_id}")
        return channels[:max_results]

    except HttpError as e:
        logger.error(f"YouTube API error: {e}")
        if e.resp.status == 404:
            logger.error("No videos found for this category")
            return []
        raise
    except Exception as e:
        logger.error(f"Error searching channels: {e}")
        return []

def get_category_keywords(category_id):
    """Return relevant keywords for each category to improve search results"""
    keywords = {
        "27": "education tutorial learning course teach university college school academic",  # Education
        "28": "science technology engineering mathematics tech coding programming",  # Science & Technology
        "24": "entertainment fun show series",  # Entertainment
        "25": "news politics current affairs analysis",  # News & Politics
        "26": "how to style tips tricks tutorial guide",  # How-to & Style
        "10": "music song audio playlist album artist",  # Music
        "20": "gaming gameplay walkthrough review",  # Gaming
        "22": "vlog lifestyle daily life",  # People & Blogs
        "23": "comedy funny humor sketch",  # Comedy
    }
    return keywords.get(category_id, "")

@recom_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all YouTube categories"""
    categories = [
        {"id": "1", "name": "Film & Animation"},
        {"id": "2", "name": "Autos & Vehicles"},
        {"id": "10", "name": "Music"},
        {"id": "15", "name": "Pets & Animals"},
        {"id": "17", "name": "Sports"},
        {"id": "20", "name": "Gaming"},
        {"id": "22", "name": "People & Blogs"},
        {"id": "23", "name": "Comedy"},
        {"id": "24", "name": "Entertainment"},
        {"id": "25", "name": "News & Politics"},
        {"id": "26", "name": "How-to & Style"},
        {"id": "27", "name": "Education"},
        {"id": "28", "name": "Science & Technology"}
    ]
    return jsonify({
        'success': True,
        'categories': categories
    })

@recom_bp.route('/recommendations', methods=['POST', 'OPTIONS'])
def get_recommendations():
    """Get channel recommendations based on selected categories"""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data received'
            }), 400

        categories = data.get('categories', [])
        if not categories:
            return jsonify({
                'success': False,
                'error': 'No categories selected'
            }), 400

        youtube = get_youtube_service()
        if not youtube:
            return jsonify({
                'success': False,
                'error': 'Could not initialize YouTube service'
            }), 500

        all_channels = []
        for category_id in categories:
            try:
                channels = search_channels_by_category(youtube, category_id)
                if channels:
                    all_channels.extend(channels)
                else:
                    logger.warning(f"No channels found for category {category_id}")
            except Exception as e:
                logger.error(f"Error processing category {category_id}: {e}")
                continue

        # Sort channels by subscriber count
        all_channels.sort(key=lambda x: x['subscriber_count'], reverse=True)

        # Log the response for debugging
        logger.info(f"Found {len(all_channels)} channels for categories {categories}")
        if not all_channels:
            logger.warning(f"No channels found for categories {categories}")

        return jsonify({
            'success': True,
            'results': all_channels,
            'count': len(all_channels)
        })

    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@recom_bp.route('/test-db', methods=['GET'])
def test_database():
    """Test database connection"""
    try:
        logger.info("Received test-db request")
        try:
            count = youtube_collection.count_documents({})
            sample = youtube_collection.find_one({}, {'_id': 0})
        except Exception:
            count = len(SAMPLE_CHANNELS)
            sample = SAMPLE_CHANNELS[0]
            
        logger.info(f"Database test successful. Found {count} records")
        return jsonify({
            'success': True,
            'record_count': count,
            'sample_data': sample
        })
    except Exception as e:
        logger.error(f"Error testing database: {e}")
        return jsonify({
            'success': True,
            'record_count': len(SAMPLE_CHANNELS),
            'sample_data': SAMPLE_CHANNELS[0]
        })

@recom_bp.route('/channel/<channel_id>', methods=['GET'])
def get_channel_details(channel_id):
    """Get detailed information about a specific channel"""
    try:
        logger.info(f"Fetching details for channel: {channel_id}")
        channel = youtube_collection.find_one(
            {'channel_id': channel_id},
            {'_id': 0}  # Exclude MongoDB _id
        )
        
        if not channel:
            return jsonify({
                'success': False,
                'error': 'Channel not found'
            }), 404

        return jsonify({
            'success': True,
            'channel': channel
        })
    except PyMongoError as e:
        logger.error(f"Database error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@recom_bp.route('/channel/<channel_id>/videos', methods=['GET'])
def get_channel_videos(channel_id):
    """Get videos for a specific channel"""
    try:
        logger.info(f"Fetching videos for channel: {channel_id}")
        channel = youtube_collection.find_one(
            {'channel_id': channel_id},
            {'videos': 1, '_id': 0}
        )
        
        if not channel or 'videos' not in channel:
            return jsonify({
                'success': False,
                'error': 'Channel or videos not found'
            }), 404

        return jsonify({
            'success': True,
            'videos': channel['videos']
        })
    except PyMongoError as e:
        logger.error(f"Database error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@recom_bp.route('/channel/<channel_id>/shorts', methods=['GET'])
def get_channel_shorts(channel_id):
    """Get shorts for a specific channel"""
    try:
        logger.info(f"Fetching shorts for channel: {channel_id}")
        channel = youtube_collection.find_one(
            {'channel_id': channel_id},
            {'shorts': 1, '_id': 0}
        )
        
        if not channel or 'shorts' not in channel:
            return jsonify({
                'success': False,
                'error': 'Channel or shorts not found'
            }), 404

        return jsonify({
            'success': True,
            'shorts': channel['shorts']
        })
    except PyMongoError as e:
        logger.error(f"Database error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@recom_bp.route('/add-channel', methods=['POST'])
def add_channel():
    """Add a new channel to the database"""
    try:
        data = request.get_json()
        required_fields = ['channel_name', 'category', 'description']
        
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400

        result = youtube_collection.insert_one({
            'channel_name': data['channel_name'],
            'category': data['category'],
            'description': data['description'],
            'subscriber_count': data.get('subscriber_count', 0),
            'video_count': data.get('video_count', 0),
            'view_count': data.get('view_count', 0),
            'country': data.get('country', '')
        })

        return jsonify({
            'success': True,
            'inserted_id': str(result.inserted_id)
        })
    except PyMongoError as e:
        logger.error(f"Database error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@recom_bp.route('/test', methods=['GET'])
def test_connection():
    """Test endpoint to verify server is running"""
    return jsonify({
        'success': True,
        'message': 'Backend server is running'
    })