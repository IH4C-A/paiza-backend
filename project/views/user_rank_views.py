from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from project.models import User, Rank, User_rank
from flask_login import login_user
from project import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

user_rank_bp = Blueprint('user_rank', __name__)

# Userランク一覧取得
@user_rank_bp.route('/user_ranks', methods=['GET'])
@jwt_required()
def get_user_ranks():
    """
    ユーザーのランク一覧を取得するエンドポイント
    """
    user_id = get_jwt_identity()
    user_ranks = User_rank.query.filter_by(user_id=user_id).all()
    
    user_rank_list = []
    for user_rank in user_ranks:
        rank = Rank.query.get(user_rank.rank_id)
        user_rank_data = {
            'user_rank_id': user_rank.user_rank_id,
            'user_id': user_rank.user_id,
            'rank_id': user_rank.rank_id,
            'rank_code': user_rank.rank_code,
            'rank_name': rank.rank_name if rank else None
        }
        user_rank_list.append(user_rank_data)
    
    return jsonify(user_rank_list), 200

# Userランク登録
@user_rank_bp.route('/user_rank', methods=['POST'])
@jwt_required()
def register_user_rank():
    """
    ユーザーがランクを登録するエンドポイント
    """
    data = request.get_json()
    user_id = get_jwt_identity()
    
    rank_id = data.get("rank_id")
    rank_code = data.get("rank_code")
    
    if not rank_id:
        return jsonify({"error": "rank_id is required."}), 400
    
    # 既に登録されているか確認
    existing_user_rank = User_rank.query.filter_by(user_id=user_id, rank_id=rank_id, rank_code=rank_code).first()
    if not existing_user_rank:
        new_user_rank = User_rank(
            user_id=user_id,
            rank_id=rank_id,
            rank_code=rank_code,
        )
        db.session.add(new_user_rank)
        db.session.commit()
        return jsonify({
            "id": new_user_rank.user_rank_id,
            "user_id": new_user_rank.user_id,
            "rank": new_user_rank.rank_code,
            # 必要なフィールドを追加
        }), 201

    else:
        return jsonify({"error": "User rank already exists."}), 400
    

# Userランク更新
@user_rank_bp.route('/user_rank/<string:rank_id>', methods=['PUT'])
@jwt_required()
def update_user_rank(rank_id):
    """
    ユーザーのランクを更新するエンドポイント
    """
    user_id = get_jwt_identity()
    user_rank = User_rank.query.filter_by(user_id=user_id, rank_id=rank_id).first()
    
    if not user_rank:
        return jsonify({"error": "User rank not found."}), 404
    
    data = request.get_json()
    new_rank_id = data.get('rank_id', user_rank.rank_id)
    
    
    # ランクIDの更新
    user_rank.rank_id = new_rank_id
    db.session.commit()
    
    return jsonify(new_rank_id), 200