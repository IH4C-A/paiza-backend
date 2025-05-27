from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from project.models import Comment
from project import db
from datetime import datetime
import os

comment_bp = Blueprint('commnt', __name__)


# Comment一覧取得
@comment_bp.route('/comments', methods=['GET'])
def get_comments():
    comments = Comment.query.all()
    comment_list = []
    for comment in comments:
        comment_data = {
            'comment_id': comment.comment_id,
            'board_id': comment.board_id,
            'user_id': comment.user_id,
            'content': comment.content,
            'is_answered':comment.is_answered,
            'created_at':comment.created_at
        }
        comment_list.append(comment_data)
    return jsonify(comment_list), 200

# comment登録
@comment_bp.route('/comment', methods=['POST'])
def register_comment():
    data = request.get_json()
    board_id = data.get('board_id')
    user_id = data.get('user_id')
    content = data.get('content')
    is_answered = data.get('0')
    created_at = data.get('created_at')

    if not board_id or not user_id or not content:
        return jsonify({"error": "board_id, user_id, content are required."}), 400
 
    new_comment = Comment(
        board_id=board_id,
        user_id=user_id,
        content=content,
        is_answered=is_answered,        
        created_at=created_at        
    )

    db.session.add(new_comment)
    db.session.commit()

    return jsonify({
        'comment_id': new_comment.comment_id,
        'board_id': new_comment.board_id,
        'user_id': new_comment.user_id,
        'content': new_comment.content,
        'is_answered': new_comment.is_answered,
        'created_at':new_comment.created_at}), 201
    
# comment編集
@comment_bp.route('/comment/<comment_id>', methods=['PUT'])
def update_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"error": "Comment not found."}), 404

    data = request.get_json()
    comment.content = data.get('content', comment.content)
    comment.created_at = data.get('createt_at', comment.created_at)

    db.session.commit()

    return jsonify({"message": "User updated successfully!"})

# comment削除
@comment_bp.route('/comments/<comment_id>', methods=['DELETE'])
def delete_comments(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"error": "Comment not found."}), 404

    db.session.delete(comment)
    db.session.commit()

    return jsonify({"message": "Comment deleted successfully!"})