from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from project.models import Article, User, ArticleCategory, Category
from flask_login import login_user
from project import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

articlecategory_bp = Blueprint('articlecategory', __name__)

# 記事カテゴリ一覧取得
@articlecategory_bp.route('/articlecategories', methods=['GET'])
@jwt_required()
def get_article_categories():
    """
    記事のカテゴリ一覧を取得するエンドポイント
    """
    categories = ArticleCategory.query.all()
    
    category_list = []
    for category in categories:
        category_data = {
            'category_id': category.category_id,
            'category_name': category.category_name,
        }
        category_list.append(category_data)
    return jsonify(category_list), 200


# カテゴリーIDを指定して記事一覧取得
@articlecategory_bp.route('/articles/category/<string:category_id>', methods=['GET'])
@jwt_required()
def get_articles_by_category(category_id):
    """
    特定のカテゴリIDに基づいて記事の一覧を取得するエンドポイント
    """
    articlecategory = ArticleCategory.query.filter_by(category_id=category_id).all()
    
    articles = Article.query.filter(Article.article_id.in_([ac.article_id for ac in articlecategory])).all()
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