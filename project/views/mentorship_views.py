from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from project.models import Mentorship, MentorshipRequest, User, User_category, User_rank
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
    自分のメンターシップ一覧と、
    自分と同じカテゴリかつ mentor ランクを持つ学生メンター一覧を取得する
    """
    user_id = get_jwt_identity()

    # 自分のメンターシップ一覧
    mentorships = Mentorship.query.filter_by(mentee_id=user_id).all()
    mentorship_list = []
    for mentorship in mentorships:
        mentorship_data = {
            'mentorship_id': mentorship.mentorship_id,
            'mentor_id': mentorship.mentor_id,
            'mentee_id': mentorship.mentee_id,
            'started_at': mentorship.started_at.isoformat()
        }
        mentorship_list.append(mentorship_data)

    # 自分のカテゴリ一覧（IDのみ抽出）
    own_category_ids = db.session.query(User_category.category_id).filter_by(user_id=user_id).subquery()

    # 同じカテゴリに属している他のユーザーのうち、mentorランクを持つユーザー
    mentor_users = (
        db.session.query(User)
        .join(User_category, User.user_id == User_category.user_id)
        .join(User_rank, User.user_id == User_rank.user_id)
        .filter(
            User_category.category_id.in_(own_category_ids),
            User_rank.rank_code == 'mentor',
            User.user_id != user_id  # 自分自身を除外
        )
        .distinct()
        .all()
    )

    # mentorユーザーの情報整形
    student_mentors = []
    for user in mentor_users:
        student_mentors.append({
            'user_id': user.user_id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'profile_image': user.profile_image,
            'username': user.username,
        })

    return jsonify({
        'mentorships': mentorship_list,
        'student_mentors': student_mentors,
    }), 200


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

# メンター検索
@mentorship_bp.route('/mentors/search', methods=['GET'])
@jwt_required()
def search_mentors():
    current_user_id = get_jwt_identity()
    
    # 自分のカテゴリを取得
    my_category_ids = db.session.query(User_category.category_id).filter_by(user_id=current_user_id).subquery()

    # 同じカテゴリ & mentorランクのユーザーを取得
    mentors = (
        db.session.query(User)
        .join(User_category, User.user_id == User_category.user_id)
        .join(User_rank, User.user_id == User_rank.user_id)
        .filter(User_category.category_id.in_(my_category_ids))
        .filter(User_rank.rank_code == "mentor")
        .filter(User.user_id != current_user_id)
        .distinct()
        .all()
    )

    mentor_list = [{
        "user_id": m.user_id,
        "first_name": m.first_name,
        "profile_image": m.profile_image
    } for m in mentors]

    return jsonify(mentor_list), 200

# メンター申請リクエストAPI
@mentorship_bp.route('/mentorship/request', methods=['POST'])
@jwt_required()
def send_mentorship_request():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    mentor_id = data.get("mentor_id")
    message = data.get("message", "")

    existing = MentorshipRequest.query.filter_by(
        mentee_id=current_user_id,
        mentor_id=mentor_id,
        status="pending"
    ).first()
    if existing:
        return jsonify({"error": "すでに申請中です"}), 400

    new_request = MentorshipRequest(
        mentee_id=current_user_id,
        mentor_id=mentor_id,
        message=message
    )
    db.session.add(new_request)
    db.session.commit()
    return jsonify({"message": "申請を送信しました"}), 201

# 承認・メンター登録API
@mentorship_bp.route('/mentorship/request/<request_id>/approve', methods=['POST'])
@jwt_required()
def approve_mentorship(request_id):
    mentor_id = get_jwt_identity()
    req = MentorshipRequest.query.get(request_id)

    if not req or req.mentor_id != mentor_id:
        return jsonify({"error": "権限がありません"}), 403

    req.status = "approved"
    db.session.commit()

    # Mentorship作成
    new_mentorship = Mentorship(
        mentor_id=mentor_id,
        mentee_id=req.mentee_id
    )
    db.session.add(new_mentorship)
    db.session.commit()

    return jsonify({"message": "申請を承認しました"}), 200
