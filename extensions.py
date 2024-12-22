from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_redis import FlaskRedis
# from flask_login import LoginManager


db = SQLAlchemy()
cors = CORS()
jwt_manager = JWTManager()
redis_client = FlaskRedis()
# login_manager = LoginManager()
