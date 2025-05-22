import base64
from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from project.models import Chats, GroupChat, User
from flask_socketio import SocketIO, disconnect, emit
from project import db, socket
from datetime import datetime
from werkzeug.utils import secure_filename
import os

chats_bp = Blueprint('chats', __name__)


@socket.on('connect')
def handle_connect():
    try:
        token = request.args.get('token')
        if token:
            decoded_token = decoded_token(token)
            user_identity = decoded_token['sub']
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
    


    # メッセージ送信をクライアントに通知
    emit('receive_message', {
        'message': new_message.message,
        'image': new_message.image,
        'sender': new_message.sender.user_name if new_message.sender else 'Unknown',
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
        'sender': chat.sender.user_name if chat.sender else 'Unknown',
        'receiver': chat.receiver.user_name if chat.receiver else 'Unknown',
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
                'sender_name': user.user_name,  # 送信者の名前
                'profile_image': user.prof_image  # 送信者のプロフィール画像
            })
        
        return jsonify(result), 200
    
    else:
        return jsonify({"error": "group_id is required"}), 400

# チャットしたことのあるユーザーを取得、チャット履歴順にソート
@chats_bp.route('/chat_users', methods=['GET'])
@jwt_required()
def get_chat_users():
    current_user_id = get_jwt_identity()
    
    # チャット履歴を取得
    chat_users = db.session.query(Chats.receiver_user_id, User).join(User, Chats.receiver_user_id == User.user_id).filter(
        Chats.send_user_id == current_user_id
    ).order_by(Chats.chat_at.desc()).distinct().all()
    
    # チャットユーザーをJSON形式で返す
    return jsonify([{
        'user_id': user.receiver_user_id,
        'user_name': user.user_name,
        'profile_image': user.prof_image
    } for user in chat_users]), 200
