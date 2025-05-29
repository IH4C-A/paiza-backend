from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from project.models import StudyLogs, User
from flask_login import login_user
from project import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os


studylogs_bp = Blueprint('studylogs', __name__)

# 学習ログ一覧取得
@studylogs_bp.route('/studylogs', methods=['GET'])
@jwt_required()
def get_study_logs():
    """
    ユーザーの学習ログ一覧を取得するエンドポイント
    """
    user_id = get_jwt_identity()
    study_logs = StudyLogs.query.filter_by(user_id=user_id).all()
    
    log_list = []
    for log in study_logs:
        log_data = {
            'log_id': log.log_id,
            'user_id': log.user_id,
            'course_id': log.course_id,
            'study_time': log.study_time,
            'study_date': log.study_date.isoformat() if log.study_date else None,
        }
        log_list.append(log_data)
    
    return jsonify(log_list), 200

# 学習ログ登録
@studylogs_bp.route('/studylogs', methods=['POST'])
@jwt_required()
def register_study_log():
    """
    ユーザーが学習ログを登録するエンドポイント
    """
    data = request.get_json()
    course_id = data.get("course_id")
    study_time = data.get("study_time")
    
    user_id = get_jwt_identity()
    
    # 学習ログの新規登録
    new_log = StudyLogs(
        user_id=user_id,
        course_id=course_id,
        study_time=study_time,
        study_date=datetime.utcnow().isoformat()
    )
    
    db.session.add(new_log)
    db.session.commit()
    
    return jsonify(new_log), 201

# 学習ログ詳細取得
@studylogs_bp.route('/studylogs/<string:course_id>', methods=['GET'])
@jwt_required()
def get_study_log(log_id):
    """
    学習ログの詳細を取得するエンドポイント
    """
    log = StudyLogs.query.get(log_id)
    if not log:
        return jsonify({"error": "Study log not found."}), 404
    
    log_data = {
        'log_id': log.log_id,
        'user_id': log.user_id,
        'course_id': log.course_id,
        'study_time': log.study_time,
        'study_date': log.study_date.isoformat() if log.study_date else None,
    }
    
    return jsonify(log_data), 200

# 学習ログ更新
@studylogs_bp.route('/studylogs/<string:log_id>', methods=['PUT'])
@jwt_required()
def update_study_log(log_id):
    """
    学習ログを更新するエンドポイント
    """
    log = StudyLogs.query.get(log_id)
    if not log:
        return jsonify({"error": "Study log not found."}), 404
    
    data = request.get_json()
    log.course_id = data.get('course_id', log.course_id)
    log.study_time = data.get('study_time', log.study_time)
    log.study_date = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({"message": "Study log updated successfully!"}), 200