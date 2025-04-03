from pymongo import MongoClient
from blueprints.config import MONGODB_URI
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mongodb_connection():
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI)
        
        # Test the connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB!")
        
        # Get the database and collection
        db = client["network"]
        youtube_collection = db["youtube"]
        
        # Count documents
        count = youtube_collection.count_documents({})
        logger.info(f"Found {count} documents in the collection")
        
        # Get sample document
        sample = youtube_collection.find_one({}, {'_id': 0})
        if sample:
            logger.info("Sample document:")
            for key, value in sample.items():
                logger.info(f"{key}: {value}")
        else:
            logger.info("No documents found in the collection")
            
        # Get distinct categories
        categories = youtube_collection.distinct('category')
        logger.info(f"Found categories: {categories}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing MongoDB connection: {e}")
        return False

if __name__ == "__main__":
    test_mongodb_connection() 