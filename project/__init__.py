from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
import os
from datetime import timedelta
from dotenv import load_dotenv

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
cors = CORS()
jwt = JWTManager()
socket = SocketIO()
blacklist = set()

load_dotenv()

def create_app(config_filename="config.py"):
    app = Flask(__name__)
    app.config.from_pyfile(config_filename)
    app.config['DEBUG'] = True
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    cors.init_app(app)
    jwt.init_app(app)
    socket.init_app(app, cors_allowed_origins="*")

    app.config['SECRET_KEY'] = 'moyamoya_house'
    app.config['JWT_SECRET_KEY'] = 'moyamoya_house'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # 画像アップロードの設定
    app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), 'project/static/prof_image/')

    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

    from project.models import Category, User, School_info, Rank, Problem, User_category, User_rank, GroupMember

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from .views import register_blueprints
    register_blueprints(app)
    return app
