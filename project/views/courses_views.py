from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from project.models import Courses
from flask_login import login_user
from project import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

courses_bp = Blueprint('courses', __name__)

# コース一覧取得
@courses_bp.route('/courses', methods=['GET'])
def get_courses():
    """
    コースの一覧を取得するエンドポイント
    """
    courses = Courses.query.all()
    course_list = []
    for course in courses:
        course_data = {
            'course_id': course.course_id,
            'course_name': course.course_name,
            'course_description': course.description,
            'category_id': course.category_id,
            'created_at': course.created_at.isoformat(),
            'updated_at': course.updated_at.isoformat()
        }
        course_list.append(course_data)
    return jsonify(course_list), 200

# コース詳細取得
@courses_bp.route('/courses/<string:course_id>', methods=['GET'])
def get_course(course_id):
    """
    特定のコースの詳細を取得するエンドポイント
    """
    course = Courses.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found."}), 404

    course_data = {
        'course_id': course.course_id,
        'course_name': course.course_name,
        'category_id': course.category_id,
        'description': course.description,
        'created_at': course.created_at.isoformat(),
        'updated_at': course.updated_at.isoformat()
    }
    return jsonify(course_data), 200

# Category_idを指定してコース一覧取得
@courses_bp.route('/courses/category/<string:category_id>', methods=['GET'])
def get_courses_by_category(category_id):
    """
    特定のカテゴリIDに基づいてコースの一覧を取得するエンドポイント
    """
    courses = Courses.query.filter_by(category_id=category_id).all()
    course_list = []
    for course in courses:
        course_data = {
            'course_id': course.course_id,
            'course_name': course.course_name,
            'category_id': course.category_id,
            'description': course.description,
            'created_at': course.created_at.isoformat(),
            'updated_at': course.updated_at.isoformat()
        }
        course_list.append(course_data)
    return jsonify(course_list), 200

# コース登録
@courses_bp.route('/courses', methods=['POST'])
def register_course():
    """
    新しいコースを登録するエンドポイント
    """
    data = request.get_json()
    course_name = data.get('course_name')
    description = data.get('description')
    category_id = data.get('category_id')

    if not course_name or not description or not category_id:
        return jsonify({"error": "Title, description, and category_id are required."}), 400

    new_course = Courses(
        course_name=course_name,
        description=description,
        category_id=category_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.session.add(new_course)
    db.session.commit()

    return jsonify({"message": "Course registered successfully."}), 201