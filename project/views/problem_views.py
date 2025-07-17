from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy.sql.expression import func
from project.models import Problem, User_category, User_rank
from flask_login import login_user
from project import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os


problem_bp = Blueprint('problem', __name__)


@problem_bp.route('/problems', methods=['GET'])
@jwt_required()
def get_user_specific_problems():
    user_id = get_jwt_identity()

    # ユーザーのカテゴリとランクを取得
    user_categories = User_category.query.filter_by(user_id=user_id).all()
    # user_ranks = User_rank.query.filter_by(user_id=user_id).all() # これは使わないか、特定用途に限定する

    category_ids = [uc.category_id for uc in user_categories]
    mentee_rank = User_rank.query.filter_by(rank_code="student").first() # または rank_name="Beginner", "初級" など

    if not mentee_rank:
        # メンティー用ランクが見つからない場合のエラーハンドリング
        return jsonify({"msg": "Mentee rank not found in database."}), 404

    mentee_rank_id = mentee_rank.rank_id

    problems = []

    if category_ids:
        # カテゴリーがある場合：category_id × メンティー用rank_id で一致
        problems = Problem.query.filter(
            Problem.category_id.in_(category_ids),
            Problem.rank_id == mentee_rank_id # メンティー用ランクIDに固定
        ).all()
    else:
        # カテゴリー未設定 → メンティー用ランクの問題をランダムに10件取得
        problems = Problem.query.filter(
            Problem.rank_id == mentee_rank_id # メンティー用ランクIDに固定
        ).order_by(func.random()).limit(10).all()

    # category・rank をネストした形式で返す
    problem_list = []
    for p in problems:
        problem_data = {
            "problem_id": p.problem_id,
            "problem_title": p.problem_title,
            "problem_text": p.problem_text,
            "category": {
                "category_id": p.category.category_id,
                "category_name": p.category.category_name,
                "category_code": p.category.category_code
            },
            "rank": {
                "rank_id": p.rank.rank_id,
                "rank_name": p.rank.rank_name
            }
        }
        problem_list.append(problem_data)

    return jsonify(problem_list), 200
@problem_bp.route('/problem/<problem_id>', methods=['GET'])
def get_problem(problem_id):
    problem = Problem.query.get(problem_id)
    if not problem:
        return jsonify({"error": "problem not found."}), 404

    answer_data = {
        'problem_id': problem.problem_id,
        'problem_title': problem.problem_title,
        'problem_text': problem.problem_text,
        "category": {
            "category_id": problem.category.category_id,
            "category_name": problem.category.category_name,
            "category_code": problem.category.category_code
        },
        "rank": {
            "rank_id": problem.rank.rank_id,
            "rank_name": problem.rank.rank_name
        },
        "test_cases": [
            {
                "test_case_id": tc.test_case_id,
                "input_text": tc.input_text,
                "expected_output": tc.expected_output,
                "is_public": tc.is_public
            }
            for tc in problem.test_cases  # ← backref により取得可
        ]
    }

    return jsonify(answer_data), 200


# problem登録
@problem_bp.route('/problem', methods=['POST'])
def register_problem():
    data = request.get_json()
    problem_title = data.get('problem_title')
    problem_text = data.get('problem_text')
    category_id = data.get('category_id')
    rank_id = data.get('rank_id')

    if not problem_text or not category_id :
        return jsonify({"error": "problem_text, category_id are required."}), 400

    new_problem = Problem(
        problem_title=problem_title,
        problem_text=problem_text,
        category_id=category_id,
        rank_id=rank_id
    )

    db.session.add(new_problem)
    db.session.commit()

    return jsonify({
        'problem_id': new_problem.problem_id,
        'problem_title': new_problem.problem_title,
        'problem_text': new_problem.problem_text,
        'category_id': new_problem.category_id,
        'rank_id': new_problem.rank_id}), 201


@problem_bp.route('/problems/category/<string:category_id>', methods=['GET'])
def get_problems_by_category(category_id):
    problems = Problem.query.filter_by(category_id=category_id).all()
    if not problems:
        return jsonify({"error": "No problems found for this category."}), 404

    problem_list = []
    for problem in problems:
        problem_data = {
            "problem_id": problem.problem_id,
            "problem_title": problem.problem_title,
            "problem_text": problem.problem_text,
            "category": {
                "category_id": problem.category.category_id,
                "category_name": problem.category.category_name,
                "category_code": problem.category.category_code
            },
            "rank": {
                "rank_id": problem.rank.rank_id,
                "rank_name": problem.rank.rank_name
            }
        }
        problem_list.append(problem_data)

    return jsonify(problem_list), 200


# rank_idに紐づくproblem一覧取得
@problem_bp.route('/problem_all', methods=['GET'])
def get_problems_by_rank():
    problems = Problem.query.all()
    if not problems:
        return jsonify({"error": "No problems found for this rank."}), 404

    problem_list = []
    for problem in problems:
        problem_data = {
            'problem_id': problem.problem_id,
            'problem_text': problem.problem_text,
            'category_id': problem.category_id,
            'rank_id': problem.rank_id,
        }
        problem_list.append(problem_data)
    
    return jsonify(problem_list), 200