#boardテーブル追加:5/27近藤

from datetime import datetime
from flask import request, jsonify, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required
from project.models import Board, Board_Category, GrowthMilestone, GrowthMilestoneLog, Plant
from project import db
Board_bp = Blueprint('Board', __name__)

#boardのtable情報取得
@Board_bp.route('/boards', methods=['GET'])
def get_boards():
    boards = Board.query.all()
    board_list = []
    for board in boards:
        user_info = None
        if board.user:
            
            user_ranks = []
            for ur in board.user.user_ranks:
                user_ranks.append({
                    'user_rank_id': ur.user_rank_id,
                    'rank_id': ur.rank_id,
                    'rank_name': ur.rank.rank_name,
                    'rank_code': ur.rank_code
                })
            user_info = {
                'user_id': board.user.user_id,
                'username': board.user.first_name,
                'ranks': user_ranks
            }
        board_data = {
            'board_id': board.board_id,
            'user_id': user_info,
            'title': board.title,
            'content': board.content,
            'status': board.status,
            'created_at': board.created_at,
            'updated_at': board.updated_at,
            'comment_count': len(board.comments),
            'categories': [
                {
                    'category_id': bc.category.category_id,
                    'category_name': bc.category.category_name,
                    'category_code': bc.category.category_code
                }
                for bc in board.board_categories  # ← ここでBoard_Categoryにアクセス
            ]
        }
        board_list.append(board_data)
    return jsonify(board_list), 200


#boardの詳細取得
@Board_bp.route('/boards/<board_id>', methods=['GET'])
def get_board(board_id):
    board = Board.query.get(board_id)
    if not board:
        return jsonify({"error": "Board not found."}), 404

    user_info = None
    if board.user:
        
        user_ranks = []
        for ur in board.user.user_ranks:
            user_ranks.append({
                'user_rank_id': ur.user_rank_id,
                'rank_id': ur.rank_id,
                'rank_name': ur.rank.rank_name,
                'rank_code': ur.rank_code
            })
        user_info = {
            'user_id': board.user.user_id,
            'username': board.user.first_name,
            'ranks': user_ranks
        }
    board_data = {
        'board_id': board.board_id,
        'user_id': user_info,
        'title': board.title,
        'content': board.content,
        'status': board.status,
        'created_at': board.created_at,
        'updated_at': board.updated_at,
        'comment_count': len(board.comments),
        'categories': [
            {
                'category_id': bc.category.category_id,
                'category_name': bc.category.category_name,
                'category_code': bc.category.category_code
            }
            for bc in board.board_categories
        ]
    }
    return jsonify(board_data), 200


#boardの登録 いらない箇所あれば削る
@Board_bp.route('/board',methods=['POST'])
@jwt_required()
def register_board():
    data = request.get_json()
    title = data.get("title") 
    content = data.get("content") 
    status = data.get("status")
    category = data.get('categories',[])
    
    current_user = get_jwt_identity()

    #必須事項check 
    if not  title or not content or not status  :
        return jsonify({"error": "title, content, status, created_at and updated_at are required."}), 400
    
    new_board = Board(
    title = title ,
    user_id = current_user,
    content = content ,
    status = status ,
    
    )
    
    db.session.add(new_board)
    db.session.commit()
    
    # boardcategory登録
    for category_id in category:
        board_category = Board_Category(board_id=new_board.board_id, category_id=category_id)
        db.session.add(board_category)
    db.session.commit()
    
        # growth_milestones登録
    plant = Plant.query.filter_by(user_id = current_user).first()
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

    return jsonify ({
    'board_id': new_board.board_id ,
    'user_id' :new_board.user_id ,
    'title':new_board.title,
    'content':new_board.content,
    'status':new_board.status,
    'created_at':new_board.created_at,
    'updated_at':new_board.updated_at
    
    }),201
    
    
# board削除
@Board_bp.route('/boards/<board_id>', methods=['DELETE'])
def delete_board(board_id):
    board = Board.query.get(board_id)
    if not board:
        return jsonify({"error": "board not found."}), 404

    db.session.delete(board)
    db.session.commit()

    return jsonify({"message": "Board deleted successfully!"})