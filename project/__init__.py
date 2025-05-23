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

    # ==== ここからAPI追加 ====

    @app.route('/api/assign_ranks', methods=['POST'])
    def assign_ranks():
        data = request.json
        user_id = data.get('user_id')
        rank_ids = data.get('rank_ids', [])
        if not user_id or not rank_ids:
            return jsonify({"error": "user_idとrank_idsは必須です"}), 400
        for rank_id in rank_ids:
            db.session.add(User_rank(user_id=user_id, rank_id=rank_id))
        db.session.commit()
        return jsonify({"message": "ランクを正常に登録しました"}), 200

    @app.route('/api/add_group_members', methods=['POST'])
    def add_group_members():
        data = request.json
        group_id = data.get('group_id')
        user_ids = data.get('user_ids', [])
        if not group_id or not user_ids:
            return jsonify({"error": "group_idとuser_idsは必須です"}), 400
        for user_id in user_ids:
            db.session.add(GroupMember(group_id=group_id, user_id=user_id))
        db.session.commit()
        return jsonify({"message": "グループメンバーを正常に追加しました"}), 200

    # ==== ここまで追加 ====

    return app
