from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from project.models import Comment, GrowthMilestone, GrowthMilestoneLog, Plant, User, Board
from project import db
from datetime import datetime
import os
from project.notification import create_notification

comment_bp = Blueprint('commnt', __name__)


# Comment一覧取得
@comment_bp.route('/comments/<string:board_id>', methods=['GET'])
def get_comments(board_id):
    comments = Comment.query.filter_by(board_id=board_id).all()
    comment_list = []
    for comment in comments:
        user_info = None
        if comment.user:
            
            user_ranks = []
            for ur in comment.user.user_ranks:
                user_ranks.append({
                    'user_rank_id': ur.user_rank_id,
                    'rank_id': ur.rank_id,
                    'rank_name': ur.rank.rank_name,
                    'rank_code': ur.rank_code
                })
            user_info = {
                'user_id': comment.user.user_id,
                'username': comment.user.first_name,
                'prof_image': comment.user.profile_image,
                'ranks': user_ranks
            }
        comment_data = {
            'comment_id': comment.comment_id,
            'board_id': comment.board_id,
            'user_id': user_info,
            'content': comment.content,
            'is_answered':comment.is_answered,
            'created_at':comment.created_at
        }
        comment_list.append(comment_data)
    return jsonify(comment_list), 200

# comment登録
@comment_bp.route('/comment', methods=['POST'])
@jwt_required()
def register_comment():
    data = request.get_json()
    board_id = data.get('boardId')
    content = data.get('content')
    user_id = get_jwt_identity()

    if not board_id or not user_id or not content:
        return jsonify({"error": "board_id, user_id, content are required."}), 400
 
    new_comment = Comment(
        board_id=board_id,
        user_id=user_id,
        content=content,
        is_answered=False,
        created_at=datetime.utcnow()        
    )

    db.session.add(new_comment)
    db.session.commit()
    
    # boardの取得
    board = Board.query.get(board_id)
    # boardを投稿したユーザーの取得
    user = User.query.get(board.user_id)
    type = "Youtube"
    title = "質問への回答"
    messsage = "あなたの質問に新しい回答が投稿されました"
    priority = "medium"
    create_notification(user.user_id,title,messsage,new_comment.content,type,priority,actionurl=f'/question/{new_comment.board_id}')
    db.session.commit()
    
    # growth_milestones登録
    plant = Plant.query.filter_by(user_id = user_id).first()
    if plant:
        growth_milestone = GrowthMilestone.query.filter_by(plant_id=plant.plant_id).first() if plant else None
    if plant and growth_milestone:
        growth_milestone.milestone += 20
        db.session.commit()
        if growth_milestone.milestone >= 100:
            growth_milestone.milestone -= 100
            plant.plant_level += 1
            new_log = f"Plant level up! New level: {plant.plant_level}"
            new_milestone = GrowthMilestoneLog(
                milestone_id=growth_milestone.milestone_id,
                log_message=new_log,
                created_at=datetime.utcnow()
            )
            db.session.add(new_milestone)
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

# ベストアンサー登録
@comment_bp.route('/comments/best/<comment_id>', methods=['PUT'])
def register_best_answer(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"error": "Comment not found."}), 404

    # 既存のベストアンサーを解除
    existing_best_answer = Comment.query.filter_by(board_id=comment.board_id, is_answered=True).first()
    if existing_best_answer:
        existing_best_answer.is_answered = False
        db.session.commit()

    # 新しいベストアンサーを設定
    comment.is_answered = True
    db.session.commit()
    
    plant = Plant.query.filter_by(user_id=comment.user_id).first()
    growth_milestone = GrowthMilestone.query.filter_by(plant_id=plant.plant_id).first() if plant else None
    if plant and growth_milestone:
        growth_milestone.milestone += 20
        db.session.commit()
        if growth_milestone.milestone >= 100:
            growth_milestone.milestone -= 100
            plant.plant_level += 1
            new_log = f"Plant level up! New level: {plant.plant_level}"
            new_milestone = GrowthMilestoneLog(
                milestone_id=growth_milestone.milestone_id,
                log_message=new_log,
                created_at=datetime.utcnow()
            )
            db.session.add(new_milestone)
            db.session.commit()
    # ベストアンサー登録の通知
    
    # boardを投稿したユーザーの取得
    user = User.query.get(comment.user_id)
    type = "Youtube"
    title = "回答のベストアンサー"
    messsage = "あなたの回答がベストアンサーに選ばれました"
    priority = "medium"
    create_notification(user.user_id,title,messsage,comment.content,type,priority,actionurl=f'/question/{comment.board_id}')
    db.session.commit()

    return jsonify({"message": "Best answer registered successfully!"}), 200