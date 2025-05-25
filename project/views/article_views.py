from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from project.models import Article, User, ArticleCategory
from flask_login import login_user
from project import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

article_bp = Blueprint('article', __name__)

# 記事一覧取得
@article_bp.route('/articles', methods=['GET'])
@jwt_required()
def get_articles():
    """
    ユーザーの投稿した記事一覧を取得するエンドポイント
    """
    user_id = get_jwt_identity()
    articles = Article.query.filter_by(user_id=user_id).all()
    
    article_list = []
    for article in articles:
        article_data = {
            'article_id': article.article_id,
            'user_id': article.user_id,
            'title': article.title,
            'content': article.content,
            'created_at': article.created_at.isoformat(),
            'updated_at': article.updated_at.isoformat()
        }
        article_list.append(article_data)
    
    return jsonify(article_list), 200

# 記事登録
@article_bp.route('/articles', methods=['POST'])
@jwt_required()
def register_article():
    """
    ユーザーが記事を登録するエンドポイント
    """
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")
    category_ids = data.get("category_ids[]")  # カテゴリIDのリスト
    
    user_id = get_jwt_identity()
    
    # 記事の新規登録
    new_article = Article(
        user_id=user_id,
        title=title,
        content=content,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.session.add(new_article)
    db.session.commit()
    
    # ArticleCategory登録処理for文で
    for category_id in category_ids:
        article_category = ArticleCategory(
            article_id=new_article.article_id,
            category_id=category_id
        )
        db.session.add(article_category)
    db.session.commit()
    
    
    
    return jsonify(new_article), 201

# 記事詳細取得
@article_bp.route('/articles/<string:article_id>', methods=['GET'])
@jwt_required()
def get_article(article_id):
    """
    記事の詳細を取得するエンドポイント
    """
    article = Article.query.get(article_id)
    if not article:
        return jsonify({"error": "Article not found."}), 404
    
    article_data = {
        'article_id': article.article_id,
        'user_id': article.user_id,
        'title': article.title,
        'content': article.content,
        'created_at': article.created_at.isoformat(),
        'updated_at': article.updated_at.isoformat()
    }
    
    return jsonify(article_data), 200