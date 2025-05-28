from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from project.models import Category
from flask_login import login_user
from project import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

category_bp = Blueprint('category', __name__)

#category一覧取得
@category_bp.route('/categorys', methods=['GET'])
def get_categorys():
    categorys = Category.query.all()
    category_list = []
    for category in categorys:
        category_data = {
            'category_id': category.category_id,
            'category_name': category.category_name,
            'category_code': category.category_code
        }
        category_list.append(category_data)
    return jsonify(category_list), 200


# category詳細取得
@category_bp.route('/categorys/<category_id>', methods=['GET'])
def get_category(category_id):
    category = category.query.get(category_id)
    if not category:
        return jsonify({"error": "category not found."}), 404

    category_data = {
        'category_id': category.category_id,
        'category_name': category.category_name,
        'category_code': category.category_code
    }
    return jsonify(category_data), 200

# categoryアップデート
@category_bp.route('/categorys/<category_id>', methods=['PUT'])
def update_category(category_id):
    category = category.query.get(category_id)
    if not category:
        return jsonify({"error": "category not found."}), 404

    data = request.get_json()
    category.category_name = data.get('category_name', category.category_name)

    db.session.commit()

    return jsonify({"message": "category updated successfully!"})

# category削除
@category_bp.route('/categorys/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = category.query.get(category_id)
    if not category:
        return jsonify({"error": "category not found."}), 404

    db.session.delete(category)
    db.session.commit()

    return jsonify({"message": "category deleted successfully!"})

# category作成
@category_bp.route('/categorys', methods=['POST'])
def create_category():
    data = request.get_json()
    category_name = data.get('category_name')
    category_code = data.get('category_code')
    new_category = Category(category_name=category_name, category_code=category_code)
    db.session.add(new_category)
    db.session.commit()

    return jsonify({"message": "category created successfully!"}), 201