from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from project.models import Problem
from flask_login import login_user
from project import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os


problem_bp = Blueprint('problem', __name__)

# Problem一覧取得
@problem_bp.route('/problems', methods=['GET'])
def get_problems():
    problems = Problem.query.all()
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

# problem詳細取得
@problem_bp.route('/problem/<problem_id>', methods=['GET'])
def get_problem(problem_id):
    problem = Problem.query.get(problem_id)
    if not problem:
        return jsonify({"error": "problem not found."}), 404

    answer_data = {
            'problem_id': problem.problem_id,
            'problem_text': problem.problem_text,
            'category_id': problem.category_id,
            'rank_id': problem.rank_id,
        }
    return jsonify(answer_data), 200

# problem登録
@problem_bp.route('/problem', methods=['POST'])
def register_problem():
    data = request.get_json()
    problem_text = data.get('problem_text')
    category_id = data.get('category_id')
    rank_id = data.get('rank_id')

    if not problem_text or not category_id :
        return jsonify({"error": "problem_text, category_id are required."}), 400

    new_problem = Problem(
        problem_text=problem_text,
        category_id=category_id,
        rank_id=rank_id
    )

    db.session.add(new_problem)
    db.session.commit()

    return jsonify({
        'problem_id': new_problem.problem_id,
        'problem_text': new_problem.problem_text,
        'category_id': new_problem.category_id,
        'rank_id': new_problem.rank_id}), 201


# category_idに紐づくproblem一覧取得
@problem_bp.route('/problems/category/<string:category_id>', methods=['GET'])
def get_problems_by_category(category_id):
    problems = Problem.query.filter_by(category_id=category_id).all()
    if not problems:
        return jsonify({"error": "No problems found for this category."}), 404

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

# rank_idに紐づくproblem一覧取得
@problem_bp.route('/problems/rank/<string:rank_id>', methods=['GET'])
def get_problems_by_rank(rank_id):
    problems = Problem.query.filter_by(rank_id=rank_id).all()
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