from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from project.models import ArticleLikes, User, Article
from flask_login import login_user
from project import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

articlelikes_bp = Blueprint('articlelikes', __name__)

# 記事のいいね一覧取得
@articlelikes_bp.route('/articlelikes', methods=['GET'])
@jwt_required()
def get_article_likes():
    """
    ユーザーがいいねした記事の一覧を取得するエンドポイント
    """
    user_id = get_jwt_identity()
    article_likes = ArticleLikes.query.filter_by(user_id=user_id).all()
    
    liked_articles = []
    for like in article_likes:
        article = Article.query.get(like.article_id)
        if article:
            article_data = {
                'article_id': article.article_id,
                'user_id': article.user_id,
                'title': article.title,
                'content': article.content,
                'created_at': article.created_at.isoformat(),
                'updated_at': article.updated_at.isoformat()
            }
            liked_articles.append(article_data)
    
    return jsonify(liked_articles), 200

# 記事にいいねを登録
@articlelikes_bp.route('/articlelikes', methods=['POST'])
@jwt_required()
def register_article_like():
    """
    ユーザーが記事にいいねを登録するエンドポイント
    """
    data = request.get_json()
    article_id = data.get("article_id")
    
    user_id = get_jwt_identity()
    
    # 既にいいねしているか確認
    existing_like = ArticleLikes.query.filter_by(user_id=user_id, article_id=article_id).first()
    
    if existing_like:
        return jsonify({"message": "You have already liked this article."}), 400
    
    # 新しいいいねを登録
    new_like = ArticleLikes(
        user_id=user_id,
        article_id=article_id,
    )
    
    db.session.add(new_like)
    db.session.commit()
    
    return jsonify({
        "user_id": new_like.user_id,
        "article_id": new_like.article_id
        }), 201

# 記事のいいねを解除
@articlelikes_bp.route('/articlelikes/<string:article_id>', methods=['DELETE'])
@jwt_required()
def delete_article_like(article_id):
    """
    ユーザーが記事のいいねを解除するエンドポイント
    """
    user_id = get_jwt_identity()
    
    # いいねを取得
    like = ArticleLikes.query.filter_by(user_id=user_id, article_id=article_id).first()
    
    if not like:
        return jsonify({"error": "Like not found."}), 404
    
    db.session.delete(like)
    db.session.commit()
    
    return jsonify({"message": "Like deleted successfully."}), 200

# 記事のいいね数を取得
@articlelikes_bp.route('/articlelikes/count/<string:article_id>', methods=['GET'])
@jwt_required()
def get_article_like_count(article_id):
    """
    特定の記事のいいね数を取得するエンドポイント
    """
    current_user = get_jwt_identity()
    like = ArticleLikes.query.filter_by(article_id=article_id, user_id=current_user).first()
    like_count = ArticleLikes.query.filter_by(article_id=article_id).count()
    
    return jsonify({"article_id": article_id, "like_count": like_count, "like": like.user_id if like else None}), 200

# 指定の記事にユーザーがいいねしているかを確認
@articlelikes_bp.route('/articlelikes/check/<string:article_id>', methods=['GET'])
@jwt_required()
def check_article_like(article_id):
    """
    ログインユーザーが指定の記事にいいねしているかを判定するエンドポイント
    """
    user_id = get_jwt_identity()

    like = ArticleLikes.query.filter_by(user_id=user_id, article_id=article_id).first()

    return jsonify({
        "article_id": article_id,
        "liked": like is not None
    }), 200
