from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import jwt
import datetime
from functools import wraps

auth = Blueprint('auth', __name__)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['network']
accounts = db['accounts']

# JWT secret key
SECRET_KEY = 'your-secret-key-here'  # Change this to a secure secret key

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = accounts.find_one({'username': data['username']})
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@auth.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
    # Check if user already exists
    if accounts.find_one({'username': data['username']}):
        return jsonify({'message': 'Username already exists!'}), 400
    
    if accounts.find_one({'email': data['email']}):
        return jsonify({'message': 'Email already exists!'}), 400
    
    # Hash the password
    hashed_password = generate_password_hash(data['password'])
    
    # Create new user
    new_user = {
        'username': data['username'],
        'email': data['email'],
        'password': hashed_password
    }
    
    accounts.insert_one(new_user)
    return jsonify({'message': 'User created successfully!'}), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Find user
    user = accounts.find_one({'username': data['username']})
    if not user:
        return jsonify({'message': 'User not found!'}), 404
    
    # Check password
    if not check_password_hash(user['password'], data['password']):
        return jsonify({'message': 'Invalid password!'}), 401
    
    # Create JWT token
    token = jwt.encode({
        'username': user['username'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, SECRET_KEY)
    
    return jsonify({
        'token': token,
        'message': 'Login successful!'
    }), 200 