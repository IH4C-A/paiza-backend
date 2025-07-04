from flask import request, jsonify, Blueprint, current_app, send_from_directory
from project.models import Answer
from project import db

answer_bp = Blueprint('answer', __name__)

# Answer一覧取得
@answer_bp.route('/answers', methods=['GET'])
def get_users():
    answers = Answer.query.all()
    answer_list = []
    for answer in answers:
        answer_data = {
            'anser_id': answer.answer_id,
            'problem_id': answer.problem_id,
            'answer_text': answer.answer_text,
            'explantion': answer.explanation,
        }
        answer_list.append(answer_data)
    return jsonify(answer_list), 200

# answer詳細取得
@answer_bp.route('/answer/<string:problem_id>', methods=['GET'])
def get_answer(problem_id):
    answer = Answer.query.filter_by(problem_id = problem_id).first()
    # problem_idでAnswerを取得
    # もしAnswerが見つからなければ404エラーを返す
    if not answer:
        return jsonify({"error": "answer not found."}), 404
    answer_data = {
            'anser_id': answer.answer_id,
            'problem_id': answer.problem_id,
            'answer_text': answer.answer_text,
            'explanation': answer.explanation,
        }
    return jsonify(answer_data), 200


# answer登録
@answer_bp.route('/answer', methods=['POST'])
def register_answer():
    data = request.get_json()
    problem_id = data.get('problem_id')
    answer_text = data.get('answer')
    explanation = data.get('explanation')

    if not answer_text or not explanation :
        return jsonify({"error": "answer_text, explanation are required."}), 400

    new_answer = Answer(
        problem_id=problem_id,
        answer_text=answer_text,
        explanation=explanation
    )

    db.session.add(new_answer)
    db.session.commit()

    return jsonify({
        'answer_id': new_answer.answer_id,
        'problem_id': new_answer.problem_id,
        'answer_text': new_answer.answer_text,
        'explanation': new_answer.explanation}), 201
    
