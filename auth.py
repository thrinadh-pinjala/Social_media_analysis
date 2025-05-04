from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from pymongo import MongoClient
from bson import ObjectId

# Initialize MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['social_media_analytics']
users_collection = db['users']

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Validate input
        if not username or not email or not password:
            return jsonify({'message': 'Missing required fields'}), 400

        # Check if username already exists
        if users_collection.find_one({'username': username}):
            return jsonify({'message': 'Username already exists'}), 409

        # Check if email already exists
        if users_collection.find_one({'email': email}):
            return jsonify({'message': 'Email already exists'}), 409

        # Hash password
        hashed_password = generate_password_hash(password)

        # Create new user
        new_user = {
            'username': username,
            'email': email,
            'password': hashed_password
        }

        # Insert user into database
        result = users_collection.insert_one(new_user)

        if result.inserted_id:
            # Create access token
            access_token = create_access_token(
                identity=str(result.inserted_id),
                expires_delta=timedelta(days=1)
            )

            return jsonify({
                'message': 'User created successfully',
                'token': access_token,
                'username': username
            }), 201
        else:
            return jsonify({'message': 'Failed to create user'}), 500

    except Exception as e:
        print(f"Signup error: {str(e)}")
        return jsonify({'message': f'Error during signup: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Find user
        user = users_collection.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            access_token = create_access_token(
                identity=str(user['_id']),
                expires_delta=timedelta(days=1)
            )
            return jsonify({
                'token': access_token,
                'username': username
            }), 200
        else:
            return jsonify({'message': 'Invalid username or password'}), 401

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'message': f'Error during login: {str(e)}'}), 500

# Protected route example
@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = users_collection.find_one({'_id': ObjectId(current_user_id)})
    if user:
        return jsonify({
            'message': 'Protected route',
            'user': {
                'username': user['username'],
                'email': user['email']
            }
        }), 200
    return jsonify({'message': 'User not found'}), 404 