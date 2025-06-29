from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from project import db
from project.models import Submission
import uuid
from datetime import datetime

submission_api = Blueprint("submission_api", __name__)

# 提出の作成（保存）
@submission_api.route("/submissions", methods=["POST"])
@jwt_required()
def create_submission():
    data = request.get_json()
    user_id = get_jwt_identity()

    submission = Submission(
        submission_id=str(uuid.uuid4()),
        user_id=user_id,
        problem_id=data["problem_id"],
        code_text=data["code_text"],
        language=data["language"],
        passed=data["passed"],
        submitted_at=datetime.utcnow()
    )
    db.session.add(submission)
    db.session.commit()
    return jsonify({"message": "提出を記録しました", "submission_id": submission.submission_id}), 201

# ユーザー or 問題ごとの提出履歴一覧取得
@submission_api.route("/submissions", methods=["GET"])
@jwt_required()
def get_submissions():
    user_id = request.args.get("user_id")
    problem_id = request.args.get("problem_id")

    query = Submission.query
    if user_id:
        query = query.filter_by(user_id=user_id)
    if problem_id:
        query = query.filter_by(problem_id=problem_id)

    submissions = query.order_by(Submission.submitted_at.desc()).all()
    return jsonify([
        {
            "submission_id": s.submission_id,
            "user_id": s.user_id,
            "problem_id": s.problem_id,
            "language": s.language,
            "code_text": s.code_text,
            "passed": s.passed,
            "submitted_at": s.submitted_at.isoformat(),
        }
        for s in submissions
    ])
