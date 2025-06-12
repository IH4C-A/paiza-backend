import base64
from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from project.models import Chats, GroupChat, GroupMember, User
from flask_socketio import SocketIO, disconnect, emit
from project import db, socket
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from  project.notification import create_notification 

chats_bp = Blueprint('chats', __name__)


from flask_jwt_extended import decode_token

@socket.on('connect')
def handle_connect():
    try:
        token = request.args.get('token')
        if token:
            decoded = decode_token(token)
            user_identity = decoded['sub']
        else:
            raise Exception("Token not provided")
    
    except Exception as e:
        print(f"Error decoding token: {str(e)}")
        disconnect()



@socket.on('send_message')
def handle_send_message(data):

    filename = None
    if 'image' in data and data['image']:
        image_data = data['image']['data']
        print(image_data)
        filename = secure_filename(data['image']['filename'])
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER_CHAT'], filename)
        
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image_data.split(",")[1]))
    if 'group_id' in data and data['group_id']:  # グループIDが存在する場合のみグループチャット処理
        # グループチャットの場合
        group = GroupChat.query.get(data['group_id'])
        if not group:
            return  # グループが存在しない場合のエラーハンドリング
        new_message = Chats(
            message=data['message'],
            send_user_id=data['send_user_id'],
            image = filename,
            group_id=data['group_id'],  # グループIDを設定
            chat_at=datetime.utcnow()
        )
        
        db.session.add(new_message)
        db.session.commit()
        
        send_user = User.query.get(new_message.send_user_id)
        
        if send_user:
            group_member = GroupMember.query.filter_by(group_id=group.group_id).all()
            for member in group_member:
                if member.user_id != new_message.send_user_id:
                    title = "グループチャットで返信"
                    type = "group_mention"
                    priority = "medium"
                    context = f'{send_user.first_name}がグループ「{group.group_name}」に新しいメッセージを送信しました'
                    create_notification(member.user_id, title, context,new_message.message,type,priority,actionurl=f'/group/{new_message.group_id}')
            db.session.commit()
    else:
        # 個人チャットの場合
        new_message = Chats(
            message=data['message'],
            send_user_id=data['send_user_id'],
            image = filename,
            receiver_user_id=data['receiver_user_id'],
            chat_at=datetime.utcnow()
        )
    
        db.session.add(new_message)
        db.session.commit()
    
        send_user = User.query.get(new_message.send_user_id)
        if send_user:
            title = "メンターからの返信"
            context = f'{send_user.first_name}が返信しました。'
            type = "mentor_reply"
            create_notification(new_message.receiver_user_id,title,context,new_message.message,type,priority="high",actionurl=f"/chat/{new_message.send_user_id}")
            db.session.commit()


    # メッセージ送信をクライアントに通知
    emit('receive_message', {
        'message': new_message.message,
        'image': new_message.image,
        'sender': new_message.sender.user_id if new_message.sender else 'Unknown',
        'group': new_message.group.group_name if new_message.group else None,  # リレーションを使用
        'chat_at': new_message.chat_at.strftime('%Y-%m-%d %H:%M:%S')
    }, broadcast=True)


# 画像の取得
@chats_bp.route('/chat_image/<path:filename>', methods=['GET'])
def get_chat_image(filename):
    # 画像の保存先ディレクトリを指定
    upload_folder = current_app.config['UPLOAD_FOLDER_CHAT']
    
    # 画像を返す
    return send_from_directory(upload_folder, filename)


# チャット履歴取得(個人)
@chats_bp.route('/chat_history', methods=['GET'])
@jwt_required()
def get_chat_history():
    current_user_id = get_jwt_identity()
    receiver_user_id = request.args.get('receiver_user_id')
    
    # チャット履歴を取得
    chat_history = Chats.query.filter(
        ((Chats.send_user_id == current_user_id) & (Chats.receiver_user_id == receiver_user_id)) |
        ((Chats.send_user_id == receiver_user_id) & (Chats.receiver_user_id == current_user_id))
    ).order_by(Chats.chat_at).all()
    
    # チャット履歴をJSON形式で返す
    return jsonify([{
        'message': chat.message,
        'image': chat.image,
        'sender': chat.sender.first_name if chat.sender else 'Unknown',
        'receiver': chat.receiver.first_name if chat.receiver else 'Unknown',
        'chat_at': chat.chat_at.strftime('%Y-%m-%d %H:%M:%S')
    } for chat in chat_history]), 200

# チャット履歴取得(グループ)
@chats_bp.route('/chat_send_group', methods=['GET'])
@jwt_required()
def chat_send_group():
    group_id = request.args.get('group_id')
    
    if group_id:
        # グループチャットの履歴を取得し、送信者のユーザー情報を結合
        group_chat = db.session.query(Chats, User).join(User, Chats.send_user_id == User.user_id).filter(
            Chats.group_id == group_id
        ).order_by(Chats.chat_at.asc()).all()

        result = []
        for chat, user in group_chat:
            result.append({
                'message': chat.message,
                'timestamp': chat.chat_at.strftime('%Y-%m-%d %H:%M:%S'),
                'send_user_id': chat.send_user_id,
                'group_id': chat.group_id,  # グループIDを含める
                'sender_name': user.first_name,  # 送信者の名前
                'profile_image': user.profile_image  # 送信者のプロフィール画像
            })
        
        return jsonify(result), 200
    
    else:
        return jsonify({"error": "group_id is required"}), 400

from sqlalchemy.orm import aliased
from sqlalchemy.sql import func

@chats_bp.route('/chat_users', methods=['GET'])
@jwt_required()
def get_chat_users():
    current_user_id = get_jwt_identity()

    # 各相手ごとの最新チャット
    latest_chats_subq = (
        db.session.query(
            Chats.receiver_user_id,
            func.max(Chats.chat_at).label("latest_chat_at")
        )
        .filter(Chats.send_user_id == current_user_id)
        .group_by(Chats.receiver_user_id)
        .subquery()
    )

    # 自分宛の未読メッセージ件数を相手（送信者）ごとに取得
    unread_counts_subq = (
        db.session.query(
            Chats.send_user_id.label("user_id"),
            func.count().label("unread_count")
        )
        .filter(
            Chats.receiver_user_id == current_user_id,
            Chats.is_read == False
        )
        .group_by(Chats.send_user_id)
        .subquery()
    )

    ChatsAlias = aliased(Chats)

    results = (
        db.session.query(ChatsAlias, User, unread_counts_subq.c.unread_count)
        .join(
            latest_chats_subq,
            (ChatsAlias.receiver_user_id == latest_chats_subq.c.receiver_user_id) &
            (ChatsAlias.chat_at == latest_chats_subq.c.latest_chat_at)
        )
        .join(User, ChatsAlias.receiver_user_id == User.user_id)
        .outerjoin(unread_counts_subq, unread_counts_subq.c.user_id == User.user_id)
        .order_by(ChatsAlias.chat_at.desc())
        .all()
    )

    return jsonify([
        {
            "user_id": chat.receiver_user_id,
            "user_name": user.first_name,  # ← 正しい属性名に
            "profile_image": user.profile_image,
            "last_message": chat.message,
            "last_chat_at": chat.chat_at.strftime('%Y-%m-%d %H:%M:%S') if chat.chat_at else None,
            "unread_count": unread_count or 0
        }
        for chat, user, unread_count in results
    ]), 200


