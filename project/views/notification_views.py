from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from project.models import Notification, User
from flask_login import login_user
from project import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

notification_bp = Blueprint('notification', __name__)

# 通知一覧取得
@notification_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """
    ユーザーの通知一覧を取得するエンドポイント
    """
    user_id = get_jwt_identity()
    notifications = Notification.query.filter_by(user_id=user_id).all()
    
    notification_list = []
    for notification in notifications:
        notification_data = {
            'notification_id': notification.notification_id,
            'user_id': notification.user_id,
            'message': notification.message,
            'created_at': notification.created_at.isoformat(),
            'is_read': notification.is_read
        }
        notification_list.append(notification_data)
    
    return jsonify(notification_list), 200

# 未読通知数取得
@notification_bp.route('/notifications/unread_count', methods=['GET'])
@jwt_required()
def get_unread_notification_count():
    """
    ユーザーの未読通知数を取得するエンドポイント
    """
    user_id = get_jwt_identity()
    unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    
    return jsonify({'unread_count': unread_count}), 200

# 未読通知を既読にする
@notification_bp.route('/notifications/mark_as_read', methods=['POST'])
@jwt_required()
def mark_notifications_as_read():
    """
    ユーザーの未読通知を既読にするエンドポイント
    """
    user_id = get_jwt_identity()
    notifications = Notification.query.filter_by(user_id=user_id, is_read=False).all()
    
    for notification in notifications:
        notification.is_read = True
    
    db.session.commit()
    
    return jsonify({"message": "All unread notifications marked as read."}), 200

# 通知詳細取得
@notification_bp.route('/notifications/<string:notification_id>', methods=['GET'])
@jwt_required()
def get_notification(notification_id):
    """
    特定の通知の詳細を取得するエンドポイント
    """
    user_id = get_jwt_identity()
    notification = Notification.query.filter_by(notification_id=notification_id, user_id=user_id).first()
    
    if not notification:
        return jsonify({"error": "Notification not found."}), 404
    
    notification_data = {
        'notification_id': notification.notification_id,
        'user_id': notification.user_id,
        'message': notification.message,
        'created_at': notification.created_at.isoformat(),
        'is_read': notification.is_read
    }
    
    return jsonify(notification_data), 200