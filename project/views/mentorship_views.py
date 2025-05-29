from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from project.models import Mentorship, User
from flask_login import login_user
from project import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

mentorship_bp = Blueprint('mentorship', __name__)

# 自分のメンターシップ一覧取得
@mentorship_bp.route('/mentorships', methods=['GET'])
@jwt_required()
def get_mentorships():
    """
    ユーザーのメンターシップ一覧を取得するエンドポイント
    """
    user_id = get_jwt_identity()
    mentorships = Mentorship.query.filter_by(user_id=user_id).all()
    
    mentorship_list = []
    for mentorship in mentorships:
        mentorship_data = {
            'mentorship_id': mentorship.mentorship_id,
            'mentor_id': mentorship.mentor_id,
            'mentee_id': mentorship.mentee_id,
            'started_at': mentorship.started_at.isoformat()
        }
        mentorship_list.append(mentorship_data)
    
    return jsonify(mentorship_list), 200

# メンターシップ登録
@mentorship_bp.route('/mentorship', methods=['POST'])
@jwt_required()
def register_mentorship():
    """
    ユーザーがメンターシップを登録するエンドポイント
    """
    data = request.get_json()
    mentor_user = data.get("user_id")
    user_id = get_jwt_identity()

    # メンターシップの新規登録
    new_mentorship = Mentorship(
        mentee_id=user_id,
        mentor_id=mentor_user,
        started_at=datetime.utcnow()
    )
    
    db.session.add(new_mentorship)
    db.session.commit()
    
    return jsonify({"message": "Mentorship registered successfully."}), 201

# メンターシップ詳細取得
@mentorship_bp.route('/mentorships/<string:mentorship_id>', methods=['GET'])
@jwt_required()
def get_mentorship(mentorship_id):
    """
    メンターシップの詳細を取得するエンドポイント
    """
    mentorship = Mentorship.query.get(mentorship_id)
    if not mentorship:
        return jsonify({"error": "Mentorship not found."}), 404

    mentorship_data = {
        'mentorship_id': mentorship.mentorship_id,
        'mentee_id': mentorship.mentee_id,
        'mentor_id': mentorship.mentor_id,
        'started_at': mentorship.started_at.isoformat(),
        'ended_at': mentorship.ended_at.isoformat()
    }
    
    return jsonify(mentorship_data), 200

# メンターシップ削除
@mentorship_bp.route('/mentorships/<string:mentorship_id>', methods=['DELETE'])
@jwt_required()
def delete_mentorship(mentorship_id):
    """
    メンターシップを削除するエンドポイント
    """
    mentorship = Mentorship.query.get(mentorship_id)
    if not mentorship:
        return jsonify({"error": "Mentorship not found."}), 404

    db.session.delete(mentorship)
    db.session.commit()
    
    return jsonify({"message": "Mentorship deleted successfully!"}), 200