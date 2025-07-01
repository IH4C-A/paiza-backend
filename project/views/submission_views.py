from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from project import db
from project.models import Rank, Submission, User_rank
import uuid
from datetime import datetime

submission_api = Blueprint("submission_api", __name__)

@submission_api.route("/submissions", methods=["POST"])
@jwt_required()
def create_submission():
    data = request.get_json()
    user_id = get_jwt_identity()

    # 提出を保存
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

    # 正解した場合のランクアップ処理
    if data["passed"] is True:
        # 現在の user_rank を取得
        current_user_rank = User_rank.query.filter_by(user_id=user_id, rank_code="student").first()

        if current_user_rank:
            # 現在のランク名
            current_rank_name = current_user_rank.rank.rank_name

            # 昇格対象ランク（順序定義）
            rank_order = ["D", "C", "B", "A", "S"]
            if current_rank_name in rank_order and current_rank_name != "S":
                # 次のランクを取得
                next_rank_index = rank_order.index(current_rank_name) + 1
                next_rank_name = rank_order[next_rank_index]

                # 次のランクのrank_idを取得
                next_rank = Rank.query.filter_by(rank_name=next_rank_name).first()
                if next_rank:
                    # ランクを更新
                    current_user_rank.rank_id = next_rank.rank_id
                    db.session.commit()

    return jsonify({"message": "提出を記録しました", "submission_id": submission.submission_id}), 201


# ユーザー or 問題ごとの提出履歴一覧取得
@submission_api.route("/submissions", methods=["GET"])
@jwt_required()
def get_submissions():
    user_id = request.args.get("user_id")

    query = Submission.query
    if user_id:
        query = query.filter_by(user_id=user_id)

    submissions = query.order_by(Submission.submitted_at.desc()).all()

    results = []
    for s in submissions:
        p = s.problem  # Problem オブジェクト

        problem_data = {
            "problem_id": p.problem_id,
            "problem_title": p.problem_title,
            "problem_text": p.problem_text,
            "category": {
                "category_id": p.category.category_id,
                "category_name": p.category.category_name,
                "category_code": p.category.category_code,
            },
            "rank": {
                "rank_id": p.rank.rank_id,
                "rank_name": p.rank.rank_name,
            },
        }

        results.append({
            "submission_id": s.submission_id,
            "user_id": s.user_id,
            "problem_id": s.problem_id,
            "language": s.language,
            "code_text": s.code_text,
            "passed": s.passed,
            "submitted_at": s.submitted_at.isoformat(),
            "problem": problem_data,
        })

    return jsonify(results),200

