from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from project.models import User, User_category,Category
from flask_login import login_user
from project import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

user_category_bp = Blueprint('user_category', __name__)

# Userカテゴリー一覧取得
@user_category_bp.route('/user_categories', methods=['GET'])
@jwt_required()
def get_user_categories():
    """
    ユーザーが登録しているカテゴリーの一覧を取得するエンドポイント
    """
    user_id = get_jwt_identity()
    user_categories = User_category.query.filter_by(user_id=user_id).all()
    
    user_category_list = []
    for user_category in user_categories:
        category = Category.query.get(user_category.category_id)
        user_category_data = {
            'user_id': user_category.user_id,
            'category_id': user_category.category_id,
            'category_name': category.category_name if category else None
        }
        user_category_list.append(user_category_data)
    
    return jsonify(user_category_list), 200

# Userカテゴリー登録(for文で複数登録可能)
@user_category_bp.route('/user_category', methods=['POST'])
@jwt_required()
def register_user_category():
    """
    ユーザーがカテゴリーを登録するエンドポイント
    """
    data = request.get_json()
    user_id = get_jwt_identity()
    
    # カテゴリーIDのリストを取得
    category_ids = data.get("category_ids[]")
    
    if not category_ids:
        return jsonify({"error": "category_ids is required."}), 400
    
    for category_id in category_ids:
        # 既に登録されているか確認
        existing_user_category = User_category.query.filter_by(user_id=user_id, category_id=category_id).first()
        if not existing_user_category:
            new_user_category = User_category(
                user_id=user_id,
                category_id=category_id
            )
            db.session.add(new_user_category)
    
    db.session.commit()
    
    return jsonify({"message": "User categories registered successfully."}), 201

# Userカテゴリー削除
@user_category_bp.route('/user_category/<string:category_id>', methods=['DELETE'])
@jwt_required()
def delete_user_category(category_id):
    """
    ユーザーがカテゴリーを削除するエンドポイント
    """
    user_id = get_jwt_identity()
    user_category = User_category.query.filter_by(user_id=user_id, category_id=category_id).first()
    
    if not user_category:
        return jsonify({"error": "User category not found."}), 404
    
    db.session.delete(user_category)
    db.session.commit()
    
    return jsonify({"message": "User category deleted successfully."}), 200