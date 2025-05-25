from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from project.models import CourseProgress, Courses, User
from flask_login import login_user
from project import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

courseprogress_bp = Blueprint('courseprogress', __name__)

# コース進捗一覧取得
@courseprogress_bp.route('/courseprogress', methods=['GET'])
@jwt_required()
def get_course_progress():
    """
    ユーザーのコース進捗一覧を取得するエンドポイント
    """
    user_id = get_jwt_identity()
    course_progresses = CourseProgress.query.filter_by(user_id=user_id).all()
    
    progress_list = []
    for progress in course_progresses:
        course = Courses.query.get(progress.course_id)
        if course:
            progress_data = {
                'course_id': progress.course_id,
                'course_name': course.course_name,
                'progress_percentage': progress.progress_percentage,
                'last_updated': progress.last_updated.isoformat(),
            }
            progress_list.append(progress_data)
    
    return jsonify(progress_list), 200

# コース進捗登録
@courseprogress_bp.route('/courseprogress', methods=['POST'])
@jwt_required()
def register_course_progress():
    """
    ユーザーがコース進捗を登録するエンドポイント
    """
    data = request.get_json()
    course_id = data.get("course_id")
    progress_percentage = data.get("progress_percentage")
    
    user_id = get_jwt_identity()
    
    # 既存の進捗を更新または新規登録
    progress = CourseProgress.query.filter_by(user_id=user_id, course_id=course_id).first()
    
    if progress:
        progress.progress_percentage = progress_percentage
        progress.last_updated = datetime.utcnow()
    else:
        progress = CourseProgress(
            user_id=user_id,
            course_id=course_id,
            progress_percentage=progress_percentage,
            last_updated=datetime.utcnow()
        )
        db.session.add(progress)
    
    db.session.commit()
    
    return jsonify({"message": "Course progress updated successfully."}), 201

# コース進捗詳細取得
@courseprogress_bp.route('/courseprogress/<string:course_id>', methods=['GET'])
@jwt_required()
def get_course_progress_detail(course_id):
    """
    特定のコースの進捗詳細を取得するエンドポイント
    """
    user_id = get_jwt_identity()
    progress = CourseProgress.query.filter_by(user_id=user_id, course_id=course_id).first()
    
    if not progress:
        return jsonify({"error": "Course progress not found."}), 404
    
    course = Courses.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found."}), 404
    
    progress_data = {
        'course_id': progress.course_id,
        'course_name': course.course_name,
        'progress_percentage': progress.progress_percentage,
        'last_updated': progress.last_updated.isoformat(),
    }
    
    return jsonify(progress_data), 200