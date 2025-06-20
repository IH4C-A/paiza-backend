from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from project import db
from project.models import Mentorship, MentorshipSchedule
from datetime import datetime

mentor_schedule_bp = Blueprint('mentor_schedule', __name__)

# Create
@mentor_schedule_bp.route('/mentorship-schedules', methods=['POST'])
@jwt_required()
def create_schedule():
    data = request.get_json()
    schedule = MentorshipSchedule(
        mentorship_id=data['mentorship_id'],
        start_time=datetime.fromisoformat(data['start_time']),
        end_time=datetime.fromisoformat(data['end_time']),
        status=data.get('status', 'scheduled'),
        topic=data.get('topic'),
        description=data.get('description'),
        cancel_reason=data.get('cancel_reason')
    )
    db.session.add(schedule)
    db.session.commit()
    return jsonify({'schedule_id': schedule.schedule_id}), 201

# Read (list)
@mentor_schedule_bp.route('/mentorship-schedules', methods=['GET'])
@jwt_required()
def list_schedules():
    current_user_id = get_jwt_identity()

    # 該当ユーザーが関係しているMentorshipを取得
    mentorships_as_mentor = Mentorship.query.filter_by(mentor_id=current_user_id).all()
    mentorships_as_mentee = Mentorship.query.filter_by(mentee_id=current_user_id).all()

    mentorship_ids = [m.mentorship_id for m in mentorships_as_mentor + mentorships_as_mentee]
    if not mentorship_ids:
        return jsonify([])

    schedules = MentorshipSchedule.query.filter(
        MentorshipSchedule.mentorship_id.in_(mentorship_ids)
    ).order_by(MentorshipSchedule.start_time).all()

    result = []
    for s in schedules:
        mentorship = s.mentorship  # リレーションを活用
        mentor_user = mentorship.mentor
        mentee_user = mentorship.mentee

        result.append({
            'schedule_id': s.schedule_id,
            'start_time': s.start_time.isoformat(),
            'end_time': s.end_time.isoformat(),
            'status': s.status,
            'topic': s.topic,
            'description': s.description,
            'created_at': s.created_at.isoformat(),
            'updated_at': s.updated_at.isoformat(),
            'cancel_reason': s.cancel_reason,
            'meeting_link': s.meeting_link,  # meeting_linkを追加

            # メンタリング情報を展開
            'mentorship': {
                'mentorship_id': mentorship.mentorship_id,
                'mentor': {
                    'user_id': mentor_user.user_id,
                    'name': mentor_user.first_name,  # 必要に応じてカラム調整
                    'email': mentor_user.email
                },
                'mentee': {
                    'user_id': mentee_user.user_id,
                    'name': mentee_user.first_name,
                    'email': mentee_user.email
                }
            }
        })

    return jsonify(result)


# Read (single)
@mentor_schedule_bp.route('/mentorship-schedules/<schedule_id>', methods=['GET'])
@jwt_required()
def get_schedule(schedule_id):
    current_user_id = get_jwt_identity()
    
    s = MentorshipSchedule.query.get(schedule_id)
    if not s:
        return jsonify({'message': 'Schedule not found'}), 404

    mentorship = s.mentorship  # リレーションを利用
    if not mentorship:
        return jsonify({'message': 'Mentorship not found'}), 404

    # ログインユーザーがメンターまたはメンティーでなければアクセス禁止
    if current_user_id not in [mentorship.mentor_id, mentorship.mentee_id]:
        return jsonify({'message': 'Unauthorized access'}), 403

    mentor_user = mentorship.mentor
    mentee_user = mentorship.mentee

    return jsonify({
        'schedule_id': s.schedule_id,
        'mentorship_id': s.mentorship_id,
        'start_time': s.start_time.isoformat(),
        'end_time': s.end_time.isoformat(),
        'status': s.status,
        'topic': s.topic,
        'description': s.description,
        'created_at': s.created_at.isoformat(),
        'updated_at': s.updated_at.isoformat(),
        'cancel_reason': s.cancel_reason,
        'meeting_link': s.meeting_link,  # meeting_linkを追加

        'mentorship': {
            'mentorship_id': mentorship.mentorship_id,
            'mentor': {
                'user_id': mentor_user.user_id,
                'name': mentor_user.first_name,
                'email': mentor_user.email
            },
            'mentee': {
                'user_id': mentee_user.user_id,
                'name': mentee_user.first_name,
                'email': mentee_user.email
            }
        }
    })


# Update
@mentor_schedule_bp.route('/mentorship-schedules/<schedule_id>', methods=['PUT'])
@jwt_required()
def update_schedule(schedule_id):
    s = MentorshipSchedule.query.get(schedule_id)
    data = request.get_json()
    if 'start_time' in data:
        s.start_time = datetime.fromisoformat(data['start_time'])
    if 'end_time' in data:
        s.end_time = datetime.fromisoformat(data['end_time'])
    if 'status' in data:
        s.status = data['status']
    if 'topic' in data:
        s.topic = data['topic']
    if 'description' in data:
        s.description = data['description']
    if 'cancel_reason' in data:
        s.cancel_reason = data['cancel_reason']
    db.session.commit()
    return jsonify({'message': 'Updated'})

# Delete
@mentor_schedule_bp.route('/mentorship-schedules/<schedule_id>', methods=['DELETE'])
@jwt_required()
def delete_schedule(schedule_id):
    s = MentorshipSchedule.query.get(schedule_id)
    db.session.delete(s)
    db.session.commit()
    return jsonify({'message': 'Deleted'})