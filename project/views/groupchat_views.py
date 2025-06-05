from flask import request, jsonify, Blueprint, current_app, send_from_directory
from project.models import Chats, GroupChat, GroupMember, User
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from project import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

groupchat_bp = Blueprint('groupchat', __name__)

# グループチャット一覧取得
@groupchat_bp.route('/groupchats', methods=['GET'])
def get_groupchats():
    groupchats = GroupChat.query.all()
    groupchat_list = []
    for groupchat in groupchats:
        groupchat_data = {
            'group_id': groupchat.group_id,
            'group_name': groupchat.group_name,
            'group_image': groupchat.group_image,
            'create_at': groupchat.create_at,
            'create_by': groupchat.create_by
        }
        groupchat_list.append(groupchat_data)
    return jsonify(groupchat_list), 200

# グループチャット画像取得
@groupchat_bp.route('/groupchat/image/<filename>', methods=['GET'])
def get_groupchat_image(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER_GROUP'], filename)

@groupchat_bp.route('/groupchat/members/<string:group_id>', methods=['GET'])
@jwt_required()
def get_group_members(group_id):
    group = GroupChat.query.filter_by(group_id=group_id)
    if not group:
        return jsonify({'error': 'グループが見つかりません'}), 404
    
    members = db.session.query(User).join(GroupMember).filter(GroupMember.group_id == group_id).all()
    member_list = []
    for member in members:
        # ランク情報取得（複数想定。1つのみなら最初の要素を使えばOK）
        ranks = []
        for ur in member.user_ranks:
            ranks.append({
                'rank_id': ur.rank_id,
                'rank_name': ur.rank.rank_name,
                'rank_code': ur.rank_code
            })

        member_data = {
            'id': member.user_id,
            'name': member.first_name,
            'prof_image': member.profile_image,
            'rank': ranks,
        }
        member_list.append(member_data)
    
    return jsonify({'members': member_list}), 200



# グループチャット作成
@groupchat_bp.route('/groupchat', methods=['POST'])
@jwt_required()
def create_groupchat():
    data = request.get_json()
    group_name = data.get('group_name')
    group_image = data.get('group_image')
    group_description = data.get('description')
    user_ids = data.get('user_ids',[])
    
    current_user = get_jwt_identity()

    # 画像がアップロードされた場合の処理
    if group_image:
        group_image_filename = secure_filename(group_image.filename)
        group_image.save(os.path.join(current_app.config['UPLOAD_FOLDER_GROUP'], group_image_filename))
    else:
        group_image_filename = None
    
    if group_name and current_user:
        new_groupchat = GroupChat(
            group_name=group_name,
            group_image=group_image,
            create_by=current_user,
            group_description=group_description,
        )
        db.session.add(new_groupchat)
        db.session.commit()
        
    for user_id in user_ids:
        new_member = GroupMember(
            group_id=new_groupchat.group_id,
            user_id=user_id
        )
        db.session.add(new_member)
        db.session.commit()

    return jsonify(new_groupchat), 201

# 自分が所属しているグループチャット一覧取得
@groupchat_bp.route('/my_groupchats', methods=['GET'])
@jwt_required()
def get_my_groupchats():
    current_user = get_jwt_identity()
    groupchats = db.session.query(GroupChat).join(GroupMember).filter(GroupMember.user_id == current_user).all()
    
    groupchat_list = []
    for groupchat in groupchats:
        groupchat_data = {
            'group_id': groupchat.group_id,
            'group_name': groupchat.group_name,
            'group_image': groupchat.group_image,
            'create_at': groupchat.create_at,
            'group_description': groupchat.group_description,
            'create_by': groupchat.create_by
        }
        groupchat_list.append(groupchat_data)
    
    return jsonify(groupchat_list), 200

@groupchat_bp.route('/chat_groups', methods=['GET'])
@jwt_required()
def get_chat_groups():
    current_user_id = get_jwt_identity()

    # 自分が参加しているグループ一覧を取得
    groups = db.session.query(GroupChat).join(GroupMember, GroupChat.group_id == GroupMember.group_id)\
        .filter(GroupMember.user_id == current_user_id).all()

    group_list = []
    for group in groups:
        # 最新チャットを取得
        latest_chat = Chats.query.filter_by(group_id=group.group_id)\
            .order_by(Chats.chat_at.desc()).first()

        # 未読メッセージ数（自分宛のみカウント）
        unread_count = Chats.query.filter_by(group_id=group.group_id)\
            .filter(Chats.receiver_user_id == current_user_id, Chats.is_read == False)\
            .count()

        # メンバー数カウント
        member_count = GroupMember.query.filter_by(group_id=group.group_id).count()

        # カテゴリ情報（ある場合）
        category = getattr(group, 'category', None)
        category_data = {
            'id': category.id,
            'name': category.name,
        } if category else None

        group_list.append({
            'group_id': group.group_id,
            'group_name': group.group_name,
            'group_image': group.group_image,
            'created_at': group.create_at.strftime('%Y-%m-%dT%H:%M:%S'),
            'created_by': group.create_by,
            'description': group.group_description,
            # 'category': category_data,
            'last_message': latest_chat.message if latest_chat else None,
            'unread_count': unread_count,
            'member_count': member_count  # ← 追加！
        })

    return jsonify(group_list), 200

