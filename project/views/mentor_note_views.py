from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from project import db
from project.models import MentorshipNote, Mentorship, User
from datetime import datetime
import uuid

mentor_note_bp = Blueprint('mentor_note', __name__)

def note_to_dict(note):
    user = note.user  # リレーションを使用（Userとの外部キー前提）
    mentorship = note.mentorship  # Mentorshipとのリレーション        
    mentor_user = mentorship.mentor
    mentee_user = mentorship.mentee
    return {
        'note_id': note.note_id,
        'user_id': note.user_id,
        'type': note.type,
        'content': note.content,
        'created_at': note.created_at.isoformat(),
        'user': {
            'user_id': user.user_id,
            'name': user.first_name,
            'email': user.email
        } if user else None,
        # メンタリング情報を展開
        'mentorship': {
            'mentorship_id': mentorship.mentorship_id,
                'mentor': {
                    'user_id': mentor_user.user_id,
                    'name': mentor_user.first_name,  # 必要に応じてカラム調整
                    'email': mentor_user.email
                },
                'mentee': {
                    'user_id': mentorship.mentee.user_id,
                    'name': mentee_user.first_name,
                    'email': mentee_user.email
                }
            }
    }


@mentor_note_bp.route('/mentor_notes', methods=['POST'])
@jwt_required()
def create_note():
    data = request.get_json()
    user_id = get_jwt_identity()
    note = MentorshipNote(
        mentorship_id=data['mentorship_id'],
        user_id=user_id,
        type=data['type'],
        content=data['content'],
        created_at=datetime.utcnow()
    )
    db.session.add(note)
    db.session.commit()
    return jsonify(note_to_dict(note)), 201

@mentor_note_bp.route('/mentor_notes/<note_id>', methods=['GET'])
@jwt_required()
def get_note(note_id):
    note = MentorshipNote.query.get(note_id)
    return jsonify(note_to_dict(note)),200

@mentor_note_bp.route('/mentor_notes', methods=['GET'])
@jwt_required()
def list_notes():
    mentorship_id = request.args.get('mentorship_id')
    query = MentorshipNote.query
    if mentorship_id:
        query = query.filter_by(mentorship_id=mentorship_id)
    notes = query.all()
    return jsonify([note_to_dict(note) for note in notes]),200

@mentor_note_bp.route('/mentor_notes/<note_id>', methods=['PUT'])
@jwt_required()
def update_note(note_id):
    note = MentorshipNote.query.get(note_id)
    user_id = get_jwt_identity()
    if note.user_id != user_id:
        return jsonify({'msg': 'Unauthorized'}), 403
    data = request.get_json()
    note.type = data.get('type', note.type)
    note.content = data.get('content', note.content)
    db.session.commit()
    return jsonify(note_to_dict(note)),200

@mentor_note_bp.route('/mentor_notes/<note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    note = MentorshipNote.query.get(note_id)
    user_id = get_jwt_identity()
    if note.user_id != user_id:
        return jsonify({'msg': 'Unauthorized'}), 403
    db.session.delete(note)
    db.session.commit()
    return jsonify({'msg': 'Deleted'}),200