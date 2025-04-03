from flask import Flask
from flask_cors import CORS
from sentiment import sentiment_bp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/sentiment/*": {
        "origins": ["http://localhost:3000"],  # React development server
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Register blueprints
app.register_blueprint(sentiment_bp, url_prefix='/sentiment')

# Create necessary directories
os.makedirs('graphs', exist_ok=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0') 