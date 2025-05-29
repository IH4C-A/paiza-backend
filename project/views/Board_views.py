#boardテーブル追加:5/27近藤

from flask import request, jsonify, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required
from project.models import Board
from project import db
Board_bp = Blueprint('Board', __name__)

#boardのtable情報取得
@Board_bp.route('/boards',methods=['GET'])
def get_boards():
    boards = Board.query.all()
    board_list = []
    for board in boards:
        board_data = {
            'board_id': board.board_id ,
            'user_id' :board.user_id,
            'title':board.title,
            'content':board.content,
            'status':board.status,
            'created_at':board.created_at,
            'updated_at':board.updated_at
            
        }
        board_list.append(board_data)
    return jsonify(board_list),200

#boardの詳細取得
@Board_bp.route('/boards/<board_id>',methods=['GET'])
def get_board(board_id):
    board = Board.query.get(board_id)
    if not board:
        return jsonify({"error": " Board not found."}), 404
    
    board_data={
            'board_id': board.board_id ,
            'user_id' :board.user_id,
            'title':board.title,
            'content':board.content,
            'status':board.status,
            'created_at':board.created_at,
            'updated_at':board.updated_at
    }
    return jsonify(board_data),200

#boardの登録 いらない箇所あれば削る
@Board_bp.route('/board',methods=['POST'])
@jwt_required()
def register_board():
    data = request.get_json()
    title = data.get("title") 
    content = data.get("content") 
    status = data.get("status")
    
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