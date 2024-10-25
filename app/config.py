import os

class Config:
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongo_db:27017/user_db')
    SECRET_KEY = os.getenv('SECRET_KEY', 'jwt-key')