from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from project.models import Mentorship, MentorshipRequest, User, User_category, User_rank
from flask_login import login_user
from project import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from sqlalchemy import select

mentorship_bp = Blueprint('mentorship', __name__)

@mentorship_bp.route('/mentorships', methods=['GET'])
@jwt_required()
def get_mentorships():
    user_id = get_jwt_identity()

    # 🔹 自分のメンターシップ一覧
    mentorships = Mentorship.query.filter_by(mentee_id=user_id).all()
    mentorship_list = []
    mentor_user_ids = set()

    for mentorship in mentorships:
        mentor = User.query.get(mentorship.mentor_id)
        if not mentor:
            continue

        mentor_user_ids.add(mentor.user_id)

        # メンターが指導しているメンティーの数を取得
        mentees_count = Mentorship.query.filter_by(mentor_id=mentor.user_id).count()


        mentor_ranks = [{
            'user_rank_id': ur.user_rank_id,
            'rank_id': ur.rank_id,
            'rank_name': ur.rank.rank_name,
            'rank_code': ur.rank_code
        } for ur in mentor.user_ranks]

        mentor_categories = [{
            'user_category_id': uc.user_category_id,
            'category_id': uc.category_id,
            'category_name': uc.category.category_name,
            'category_code': uc.category.category_code
        } for uc in mentor.user_categories]

        mentorship_list.append({
            'mentorship_id': mentorship.mentorship_id,
            'started_at': mentorship.started_at.isoformat(),
            'mentees_count': mentees_count,
            'mentor': {
                'user_id': mentor.user_id,
                'first_name': mentor.first_name,
                'last_name': mentor.last_name,
                'profile_image': mentor.profile_image,
                'username': mentor.username,
                'ranks': mentor_ranks,
                'categories': mentor_categories,
            }
        })

    # 🔹 自分のカテゴリ一覧（リストとして取得）
    own_category_ids = db.session.query(User_category.category_id)\
        .filter(User_category.user_id == user_id).all()
    own_category_ids = [cat_id for (cat_id,) in own_category_ids]

    # 🔹 mentor候補（カテゴリあり／なしで分岐）
    if own_category_ids:
        candidate_mentors_query = (
            db.session.query(User)
            .join(User_category, User.user_id == User_category.user_id)
            .join(User_rank, User.user_id == User_rank.user_id)
            .filter(
                User_category.category_id.in_(own_category_ids),
                User_rank.rank_code == 'mentor',
                User.user_id != user_id
            )
            .distinct()
            .all()
        )
    else:
        candidate_mentors_query = (
            db.session.query(User)
            .join(User_rank, User.user_id == User_rank.user_id)
            .filter(
                User_rank.rank_code == 'mentor',
                User.user_id != user_id
            )
            .distinct()
            .all()
        )

    # ✅ 登録済み mentor を除外 & 整形
    candidate_mentors = []
    for user in candidate_mentors_query:
        if user.user_id in mentor_user_ids:
            continue
        
        # メンターが指導しているメンティーの数を取得
        mentees_count = Mentorship.query.filter_by(mentor_id=user.user_id).count()


        user_ranks = [{
            'user_rank_id': ur.user_rank_id,
            'rank_id': ur.rank_id,
            'rank_name': ur.rank.rank_name,
            'rank_code': ur.rank_code
        } for ur in user.user_ranks]

        user_categories = [{
            'user_category_id': uc.user_category_id,
            'category_id': uc.category_id,
            'category_name': uc.category.category_name,
            'category_code': uc.category.category_code
        } for uc in user.user_categories]

        candidate_mentors.append({
            'user_id': user.user_id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'profile_image': user.profile_image,
            'username': user.username,
            'ranks': user_ranks,
            'categories': user_categories,
            'mentees_count': mentees_count # ✅ 追加
        })

    return jsonify({
        'mentorship': mentorship_list,
        'student_mentors': candidate_mentors
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

@mentorship_bp.route('/mentorship/requests/received', methods=['GET'])
@jwt_required()
def get_received_mentorship_requests():
    mentor_id = get_jwt_identity()

    requests = MentorshipRequest.query.filter_by(mentor_id=mentor_id).order_by(MentorshipRequest.requested_at.desc()).all()

    result = []
    for req in requests:
        mentee = User.query.get(req.mentee_id)
            # ランク情報の取得
        user_ranks = []
        for ur in mentee.user_ranks:
            user_ranks.append({
                'user_rank_id': ur.user_rank_id,
                'rank_id': ur.rank_id,
                'rank_name': ur.rank.rank_name,
                'rank_code': ur.rank_code
            })
        
        user_category = []
        for uc in mentee.user_categories:
            user_category.append({
                'user_category_id': uc.user_category_id,
                'category_id': uc.category_id,
                'category_name': uc.category.category_name,
                'category_code': uc.category.category_code
            })
        result.append({
            "request_id": req.request_id,
            "status": req.status,
            "message": req.message,
            "requested_at": req.requested_at.isoformat(),
            "mentee": {
                'user_id': mentee.user_id,
                'first_name': mentee.first_name,
                'last_name': mentee.last_name,
                'profile_image': mentee.profile_image,
                'username': mentee.username,
                "ranks": user_ranks,
                "categories": user_category,
            }
        })

    return jsonify(result), 200

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

# 拒否API：/mentorship/request/<request_id>/reject
@mentorship_bp.route('/mentorship/request/<request_id>/reject', methods=['POST'])
@jwt_required()
def reject_mentorship_request(request_id):
    mentor_id = get_jwt_identity()
    req = MentorshipRequest.query.get(request_id)

    if not req or req.mentor_id != mentor_id:
        return jsonify({"error": "権限がありません"}), 403

    if req.status != "pending":
        return jsonify({"error": "すでに処理された申請です"}), 400

    req.status = "rejected"
    db.session.commit()

    return jsonify({"message": "申請を拒否しました"}), 200


# 全メンター取得
@mentorship_bp.route('/mentors', methods=['GET'])
@jwt_required()
def get_all_mentors():
    current_user_id = get_jwt_identity()

    mentors = (
        db.session.query(User)
        .join(User_rank, User.user_id == User_rank.user_id)
        .filter(User_rank.rank_code == "mentor", User.user_id != current_user_id)
        .all()
    )

    mentor_list = [{
        "user_id": m.user_id,
        "first_name": m.first_name,
        "last_name": m.last_name,
        "profile_image": m.profile_image,
        "username": m.username
    } for m in mentors]

    return jsonify(mentor_list), 200