from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from project.models import Rank
from flask_login import login_user
from project import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os


rank_bp = Blueprint('rank', __name__)

# rank一覧取得
@rank_bp.route('/ranks', methods=['GET'])
def get_ranks():
    ranks = Rank.query.all()
    rank_list = []
    for rank in ranks:
        rank_data = {
            'rank_id': rank.rank_id,
            'rank_name': rank.rank_name
        }
        rank_list.append(rank_data)
    return jsonify(rank_list), 200

# rank詳細取得
@rank_bp.route('/rank/<rank_id>', methods=['GET'])
def get_rank(rank_id):
    rank = Rank.query.get(rank_id)
    if not rank:
        return jsonify({"error": "Rank not found."}), 404

    rank_data = {
        'rank_id': rank.rank_id,
        'rank_name': rank.rank_name,
    }
    return jsonify(rank_data), 200

# rank登録
@rank_bp.route('/rank', methods=['POST'])
def register_rank():
    data = request.get_json()
    rank_name = data.get('rank_name')

    if not rank_name:
        return jsonify({"error": "rank_name required."}), 400
   
    new_rank = Rank(
        rank_name=rank_name
    )

    db.session.add(new_rank)
    db.session.commit()
    
    return jsonify({
        'rank_id': new_rank.rank_id,
        'username': new_rank.rank_name}), 201


# User削除
@rank_bp.route('/ranks/<rank_id>', methods=['DELETE'])
def delete_rank(rank_id):
    rank = Rank.query.get(rank_id)
    if not rank:
        return jsonify({"error": "Rank not found."}), 404

    db.session.delete(rank)
    db.session.commit()

    return jsonify({"message": "Rank deleted successfully!"})
