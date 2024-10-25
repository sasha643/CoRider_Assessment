from flask import Flask
from .routing import user_bp
from .config import Config
import redis

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.redis = redis.Redis(host="redis", port=6379, decode_responses=True)
    app.register_blueprint(user_bp, url_prefix='/api')
    return app