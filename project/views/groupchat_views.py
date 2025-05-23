from flask import request, jsonify, Blueprint, current_app, send_from_directory
from project.models import GroupChat, GroupMember, User
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

# グループチャットメンバー取得
@groupchat_bp.route('/groupchat/members/<string:group_id>', methods=['GET'])
@jwt_required()
def get_group_members(group_id):
    group = GroupChat.query.get(group_id)
    if not group:
        return jsonify({'error': 'グループが見つかりません'}), 404
    
    members = db.session.query(User).join(GroupMember).filter(GroupMember.group_id == group_id).all()
    
    member_list = [{
        'id': member.user_id,
        'name': member.username,
        'prof_image': member.profile_image,
    } for member in members]
    
    return jsonify({'members': member_list}), 200


# グループチャット作成
@groupchat_bp.route('/groupchat', methods=['POST'])
@jwt_required()
def create_groupchat():
    data = request.get_json()
    group_name = data.get('group_name')
    group_image = data.get('group_image')
    user_ids = request.json.get('user_ids[]')
    
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
            create_by=current_user
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

    return jsonify({"message": "Group chat created successfully."}), 201

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
            'create_by': groupchat.create_by
        }
        groupchat_list.append(groupchat_data)
    
    return jsonify(groupchat_list), 200