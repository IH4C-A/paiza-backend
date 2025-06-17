from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from project import db
from project.models import MentorshipFeedback, Mentorship, User
from datetime import datetime
import uuid

mentor_feedback_bp = Blueprint('mentor_feedback', __name__)

# Create feedback
@mentor_feedback_bp.route('/feedback', methods=['POST'])
@jwt_required()
def create_feedback():
    data = request.get_json()
    mentorship_id = data.get('mentorship_id')
    rating = data.get('rating')
    comment = data.get('comment', '')
    user_id = get_jwt_identity()

    if not mentorship_id or not rating:
        return jsonify({'msg': 'mentorship_id and rating are required'}), 400

    feedback = MentorshipFeedback(
        mentorship_id=mentorship_id,
        user_id=user_id,
        rating=rating,
        comment=comment,
        created_at=datetime.utcnow()
    )
    db.session.add(feedback)
    db.session.commit()
    return jsonify({'msg': 'Feedback created', 'feedback_id': feedback.feedback_id}), 201

@mentor_feedback_bp.route('/feedback', methods=['GET'])
@jwt_required()
def list_feedback():
    mentorship_id = request.args.get('mentorship_id')
    query = MentorshipFeedback.query

    if mentorship_id:
        query = query.filter_by(mentorship_id=mentorship_id)

    feedbacks = query.all()
    result = []

    for f in feedbacks:
        user = f.user  # 投稿者
        mentorship = f.mentorship  # Mentorshipオブジェクト

        # メンターとメンティー
        mentor_user = mentorship.mentor
        mentee_user = mentorship.mentee

        result.append({
            'feedback_id': f.feedback_id,
            'mentorship_id': f.mentorship_id,
            'user_id': f.user_id,
            'rating': f.rating,
            'comment': f.comment,
            'created_at': f.created_at.isoformat(),

            'user': {
                'user_id': user.user_id,
                'name': user.first_name,
                'email': user.email
            } if user else None,

            'mentorship': {
                'mentorship_id': mentorship.mentorship_id,
                'mentor': {
                    'user_id': mentor_user.user_id,
                    'name': mentor_user.first_name,
                    'email': mentor_user.email
                } if mentor_user else None,
                'mentee': {
                    'user_id': mentee_user.user_id,
                    'name': mentee_user.first_name,
                    'email': mentee_user.email
                } if mentee_user else None
            }
        })

    return jsonify(result), 200


@mentor_feedback_bp.route('/feedback/<feedback_id>', methods=['GET'])
@jwt_required()
def get_feedback(feedback_id):
    feedback = MentorshipFeedback.query.get(feedback_id)
    if not feedback:
        return jsonify({'msg': 'Feedback not found'}), 404

    user = feedback.user
    mentorship = feedback.mentorship
    mentor_user = mentorship.mentor
    mentee_user = mentorship.mentee

    return jsonify({
        'feedback_id': feedback.feedback_id,
        'mentorship_id': feedback.mentorship_id,
        'user_id': feedback.user_id,
        'rating': feedback.rating,
        'comment': feedback.comment,
        'created_at': feedback.created_at.isoformat(),

        'user': {
            'user_id': user.user_id,
            'name': user.first_name,
            'email': user.email
        } if user else None,

        'mentorship': {
            'mentorship_id': mentorship.mentorship_id,
            'mentor': {
                'user_id': mentor_user.user_id,
                'name': mentor_user.first_name,
                'email': mentor_user.email
            } if mentor_user else None,
            'mentee': {
                'user_id': mentee_user.user_id,
                'name': mentee_user.first_name,
                'email': mentee_user.email
            } if mentee_user else None
        }
    }), 200


# Update feedback
@mentor_feedback_bp.route('/feedback/<feedback_id>', methods=['PUT'])
@jwt_required()
def update_feedback(feedback_id):
    feedback = MentorshipFeedback.query.get(feedback_id)
    if not feedback:
        return jsonify({'msg': 'Feedback not found'}), 404
    user_id = get_jwt_identity()
    if feedback.user_id != user_id:
        return jsonify({'msg': 'Unauthorized'}), 403
    data = request.get_json()
    feedback.rating = data.get('rating', feedback.rating)
    feedback.comment = data.get('comment', feedback.comment)
    db.session.commit()
    return jsonify({'msg': 'Feedback updated'}),200

# Delete feedback
@mentor_feedback_bp.route('/feedback/<feedback_id>', methods=['DELETE'])
@jwt_required()
def delete_feedback(feedback_id):
    feedback = MentorshipFeedback.query.get(feedback_id)
    if not feedback:
        return jsonify({'msg': 'Feedback not found'}), 404
    user_id = get_jwt_identity()
    if feedback.user_id != user_id:
        return jsonify({'msg': 'Unauthorized'}), 403
    db.session.delete(feedback)
    db.session.commit()
    return jsonify({'msg': 'Feedback deleted'}),200