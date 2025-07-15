from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from project import db
from project.models import Mentorship, MentorshipSchedule, GroupMember, GroupChat, User
from datetime import datetime
import uuid
from project.chat_response import calculate_average_dm_response_time, get_average_mentor_rating
from project.notification import create_notification

mentor_schedule_bp = Blueprint('mentor_schedule', __name__)

# Create
@mentor_schedule_bp.route('/mentorship-schedules', methods=['POST'])
@jwt_required()
def create_schedule():
    data = request.get_json()

    mentorship_id = data.get('mentorship_id') or None
    group_id = data.get('group_id') or None

    if bool(mentorship_id) == bool(group_id):
        return jsonify({'error': 'mentorship_id または group_id のいずれか一方のみ指定してください'}), 400

    jitsi_room_name = f"mentorship-{uuid.uuid4().hex[:8]}"
    meeting_link = f"https://meet.jit.si/{jitsi_room_name}"

    schedule = MentorshipSchedule(
        mentorship_id=mentorship_id,
        group_id=group_id,
        start_time=datetime.fromisoformat(data['start_time']),
        end_time=datetime.fromisoformat(data['end_time']),
        status=data.get('status', 'scheduled'),
        topic=data.get('topic'),
        description=data.get('description'),
        cancel_reason=data.get('cancel_reason'),
        meeting_link=meeting_link,
    )
    db.session.add(schedule)
    db.session.commit()

    # 🔔 通知処理（個別 or グループ）
    try:
        title = "📅 新しい予定が作成されました"
        start_str = schedule.start_time.strftime("%Y/%m/%d %H:%M")
        message = f"{start_str} に予定があります。\n内容: {schedule.topic or '（未設定）'}"
        detail = schedule.description or ""
        actionurl = f"/schedules/{schedule.schedule_id}"  # フロントでの詳細ページURL

        if mentorship_id:
            mentorship = Mentorship.query.get(mentorship_id)
            if mentorship:
                for uid in [mentorship.mentor_id, mentorship.mentee_id]:
                    create_notification(
                        user_id=uid,
                        title=title,
                        message=message,
                        detail=detail,
                        type="task_reminder",
                        priority="normal",
                        actionurl=actionurl
                    )

        elif group_id:
            from project.models import GroupMember  # 必要に応じてインポート

            group_users = GroupMember.query.filter_by(group_id=group_id).all()
            for gu in group_users:
                create_notification(
                    user_id=gu.user_id,
                    title=title,
                    message=message,
                    detail=detail,
                    type="task_reminder",
                    priority="normal",
                    actionurl=actionurl
                )

    except Exception as e:
        print(f"スケジュール通知エラー: {e}")

    return jsonify({'schedule_id': schedule.schedule_id}), 201
# Read (list)
@mentor_schedule_bp.route('/mentorship-schedules', methods=['GET'])
@jwt_required()
def list_schedules():
    current_user_id = get_jwt_identity()

    # 個人メンタリング取得
    mentorships_as_mentor = Mentorship.query.filter_by(mentor_id=current_user_id).all()
    mentorships_as_mentee = Mentorship.query.filter_by(mentee_id=current_user_id).all()
    mentorship_ids = [m.mentorship_id for m in mentorships_as_mentor + mentorships_as_mentee]

    # グループID取得
    group_ids = db.session.query(GroupMember.group_id).filter_by(user_id=current_user_id).all()
    group_ids = [gid for (gid,) in group_ids]

    # スケジュール取得
    schedules = MentorshipSchedule.query.filter(
        (MentorshipSchedule.mentorship_id.in_(mentorship_ids)) |
        (MentorshipSchedule.group_id.in_(group_ids))
    ).order_by(MentorshipSchedule.start_time).all()

    now = datetime.utcnow()
    result = []
    for s in schedules:
        if s.start_time < now and s.status != "completed":
            s.status = "completed"
            db.session.add(s)
        item = {
            'schedule_id': s.schedule_id,
            'start_time': s.start_time.isoformat(),
            'end_time': s.end_time.isoformat(),
            'status': s.status,
            'topic': s.topic,
            'description': s.description,
            'created_at': s.created_at.isoformat(),
            'updated_at': s.updated_at.isoformat(),
            'cancel_reason': s.cancel_reason,
            'meeting_link': s.meeting_link,
        }

        if s.mentorship:
            mentor_user = s.mentorship.mentor
            mentee_user = s.mentorship.mentee
            item['mentorship_id'] = {
                'mentorship_id': s.mentorship.mentorship_id,
                'mentor': {
                    'user_id': mentor_user.user_id,
                    'first_name': mentor_user.first_name,
                    'profile_image': mentor_user.profile_image,
                },
                'mentee': {
                    'user_id': mentee_user.user_id,
                    'first_name': mentee_user.first_name,
                    'profile_image': mentee_user.profile_image,
                }
            }

        elif s.group:
            group = s.group

            group_members = (
                db.session.query(User)
                .join(GroupMember, User.user_id == GroupMember.user_id)
                .filter(GroupMember.group_id == group.group_id)
                .all()
            )
            member_list = [
                {
                    'user_id': member.user_id,
                    'first_name': member.first_name,
                    'last_name': member.last_name,
                    'email': member.email,
                    'profile_image': member.profile_image,
                }
                for member in group_members
            ]

            item['group'] = {
                'group_id': group.group_id,
                'group_name': group.group_name,
                'group_description': group.group_description,
                'group_image': group.group_image,
                'members': member_list,  # 🔸 追加
            }


        result.append(item)
    db.session.commit()
    return jsonify(result)


# Read (single)
@mentor_schedule_bp.route('/mentorship-schedules/<schedule_id>', methods=['GET'])
@jwt_required()
def get_schedule(schedule_id):
    current_user_id = get_jwt_identity()

    s = MentorshipSchedule.query.get(schedule_id)
    if not s:
        return jsonify({'message': 'Schedule not found'}), 404

    if s.mentorship:
        mentorship = s.mentorship
        if current_user_id not in [mentorship.mentor_id, mentorship.mentee_id]:
            return jsonify({'message': 'Unauthorized access'}), 403

        mentor_user = mentorship.mentor
        mentee_user = mentorship.mentee
        
        average_rating_mentor = get_average_mentor_rating(mentor_user.user_id)
        average_rating_mentee = get_average_mentor_rating(mentee_user.user_id)

        mentoruser_ranks = []
        for ur in mentor_user.user_ranks:
            mentoruser_ranks.append({
                'user_rank_id': ur.user_rank_id,
                'rank_id': ur.rank_id,
                'rank_name': ur.rank.rank_name,
                'rank_code': ur.rank_code
            })
        menteeuser_ranks = []
        for ur in mentee_user.user_ranks:
            menteeuser_ranks.append({
                'user_rank_id': ur.user_rank_id,
                'rank_id': ur.rank_id,
                'rank_name': ur.rank.rank_name,
                'rank_code': ur.rank_code
            })

        return jsonify({
            'schedule_id': s.schedule_id,
            'start_time': s.start_time.isoformat(),
            'end_time': s.end_time.isoformat(),
            'status': s.status,
            'topic': s.topic,
            'description': s.description,
            'meeting_link': s.meeting_link,
            'mentorship_id': {
                'mentorship_id': mentorship.mentorship_id,
                'mentor': {
                    'user_id': mentor_user.user_id,
                    'first_name': mentor_user.first_name,
                    'profile_image': mentor_user.profile_image,
                    'ranks': mentoruser_ranks,
                    'average_rating': average_rating_mentor,
                },
                'mentee': {
                    'user_id': mentee_user.user_id,
                    'first_name': mentee_user.first_name,
                    'profile_image': mentee_user.profile_image,
                    'ranks': menteeuser_ranks,
                    'average_rating': average_rating_mentee,
                }
            }
        })

    elif s.group:
        group = s.group

        # ログインユーザーがグループメンバーか確認
        is_member = db.session.query(GroupMember).filter_by(
            group_id=group.group_id,
            user_id=current_user_id
        ).first()
        if not is_member:
            return jsonify({'message': 'Unauthorized'}), 403

        # 🔽 グループメンバー一覧を取得
        group_members = (
            db.session.query(User)
            .join(GroupMember, User.user_id == GroupMember.user_id)
            .filter(GroupMember.group_id == group.group_id)
            .all()
        )
        member_list = [
            {
                'user_id': member.user_id,
                'first_name': member.first_name,
                'last_name': member.last_name,
                'email': member.email,
                'profile_image': member.profile_image,
            }
            for member in group_members
        ]

        return jsonify({
            'schedule_id': s.schedule_id,
            'start_time': s.start_time.isoformat(),
            'end_time': s.end_time.isoformat(),
            'status': s.status,
            'topic': s.topic,
            'description': s.description,
            'meeting_link': s.meeting_link,
            'group': {
                'group_id': group.group_id,
                'group_name': group.group_name,
                'group_description': group.group_description,
                'group_image': group.group_image,
                'members': member_list,  # 🔸 グループメンバー情報を追加
            }
        })


    return jsonify({'message': 'Invalid schedule'}), 400


# Update
@mentor_schedule_bp.route('/mentorship-schedules/<schedule_id>', methods=['PUT'])
@jwt_required()
def update_schedule(schedule_id):
    s = MentorshipSchedule.query.get(schedule_id)
    data = request.get_json()
    if not s:
        return jsonify({'message': 'Schedule not found'}), 404

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
    if not s:
        return jsonify({'message': 'Not found'}), 404
    db.session.delete(s)
    db.session.commit()
    return jsonify({'message': 'Deleted'})
