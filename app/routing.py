from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from bson.objectid import ObjectId
from app.config import Config
from redis import Redis
import jwt
import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

client = MongoClient(Config.MONGO_URI)
db = client.user_db
users_collection = db.users

redis_client = Redis(host='redis', port=6379)  

user_bp = Blueprint('user_bp', __name__)

JWT_SECRET = Config.SECRET_KEY  

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            data = jwt.decode(token.split(" ")[1], JWT_SECRET, algorithms=["HS256"])
        except Exception as e:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(*args, **kwargs)
    return decorated


def generate_tokens(user_data):
    access_token = jwt.encode({
        'user_id': str(user_data['_id']),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)  
    }, JWT_SECRET, algorithm='HS256')
    refresh_token = jwt.encode({
        'user_id': str(user_data['_id']),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)  
    }, JWT_SECRET, algorithm='HS256')
    redis_client.set(user_data['_id'], refresh_token, ex=datetime.timedelta(days=7))
    return access_token, refresh_token


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = users_collection.find_one({"email": email})
    if user and check_password_hash(user['password'], password):
        token = jwt.encode({
            'user_id': str(user['_id']),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  
        }, Config.SECRET_KEY, algorithm='HS256')
        return jsonify({'token': token}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@user_bp.route('/users', methods=['GET'])
def get_all_users():
    users = list(users_collection.find())
    for user in users:
        user["_id"] = str(user["_id"])
    return jsonify(users), 200


@user_bp.route('/users/<user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    cached_user = redis_client.get(user_id)
    if cached_user:
        return jsonify(eval(cached_user)), 200
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user["_id"] = str(user["_id"])
        redis_client.set(user_id, str(user))  
        return jsonify(user), 200
    return jsonify({"error": "User not found"}), 404


@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    data['password'] = generate_password_hash(data['password'])  
    result = users_collection.insert_one(data)
    return jsonify({"user_id": str(result.inserted_id)}), 201


@user_bp.route('/users/<user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    data = request.get_json()
    result = users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": data})
    if result.modified_count:
        redis_client.delete(user_id)
        return jsonify({"message": "User updated"}), 200
    return jsonify({"error": "User not found"}), 404


@user_bp.route('/users/<user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    result = users_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count:
        redis_client.delete(user_id)
        return jsonify({"message": "User deleted"}), 200
    return jsonify({"error": "User not found"}), 404


@user_bp.route('/refresh', methods=['POST'])
def refresh():
    data = request.get_json()
    refresh_token = data.get('refresh_token')
    if not refresh_token:
        return jsonify({'message': 'Refresh token is missing!'}), 403
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload['user_id']
        stored_refresh_token = redis_client.get(user_id)
        if stored_refresh_token and stored_refresh_token.decode('utf-8') == refresh_token:
            access_token = jwt.encode({
                'user_id': user_id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
            }, JWT_SECRET, algorithm='HS256')
            return jsonify({'access_token': access_token}), 200
        else:
            return jsonify({'message': 'Invalid refresh token'}), 403        
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Refresh token expired'}), 403
    except Exception as e:
        return jsonify({'message': 'Invalid refresh token'}), 403