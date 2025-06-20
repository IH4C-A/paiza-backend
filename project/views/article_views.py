from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from project.models import Article, ArticleLikes, GrowthMilestone, GrowthMilestoneLog, Plant, User, ArticleCategory, Category
from flask_login import login_user
from project import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

article_bp = Blueprint('article', __name__)

@article_bp.route('/articles', methods=['GET'])
@jwt_required(optional=True)  # 認証していればuser_idを取得、未認証でも取得可能
def get_articles():
    """
    ユーザーの投稿した記事一覧とカテゴリ、ユーザー詳細、いいね数、ユーザーのいいね情報を取得
    """
    user_id = get_jwt_identity()
    articles = Article.query.all()
    
    article_list = []
    for article in articles:
        # 該当記事に紐づくカテゴリ一覧
        article_categories = ArticleCategory.query.filter_by(article_id=article.article_id).all()
        categories = []
        for ac in article_categories:
            category = Category.query.filter_by(category_id=ac.category_id).first()
            if category:
                categories.append({
                    'category_id': category.category_id,
                    'category_name': category.category_name
                })

        # ユーザー情報
        user = User.query.get(article.user_id)
        user_data = {
            'user_id': user.user_id,
            'username': user.first_name,
            'email': user.email
        } if user else {}

        # いいね数
        like_count = ArticleLikes.query.filter_by(article_id=article.article_id).count()

        # ログインユーザーがこの投稿にいいねしているかどうか
        is_liked_by_user = False
        if user_id:
            is_liked_by_user = ArticleLikes.query.filter_by(article_id=article.article_id, user_id=user_id).first() is not None

        article_data = {
            'article_id': article.article_id,
            'title': article.title,
            'content': article.content,
            'created_at': article.created_at.isoformat(),
            'updated_at': article.updated_at.isoformat(),
            'user': user_data,
            'categories': categories,
            'like_count': like_count,
            'is_liked_by_user': is_liked_by_user  # 👈 ここが重要！
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
    category_ids = data.get("categoryids",[])  # カテゴリIDのリスト
    
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
    
    # growth_milestones登録
    plant = Plant.query.filter_by(user_id = user_id).first()
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
    "article_id": new_article.article_id,
    "user_id": new_article.user_id,
    "title": new_article.title,
    "content": new_article.content,
    "created_at": new_article.created_at.isoformat(),
    "updated_at": new_article.updated_at.isoformat()
}), 201


@article_bp.route('/articles/<string:article_id>', methods=['GET'])
def get_article(article_id):
    """
    記事の詳細を取得するエンドポイント（カテゴリ情報付き）
    """
    article = Article.query.get(article_id)
    if not article:
        return jsonify({"error": "Article not found."}), 404
    
        # ユーザー情報取得
    user = User.query.get(article.user_id)
    user_data = {
        'user_id': user.user_id,
        'username': user.first_name,
        'email': user.email  # 必要に応じて他の情報も含めてください
    } if user else {}

    # ArticleCategory 経由でカテゴリ一覧を取得
    article_categories = ArticleCategory.query.filter_by(article_id=article.article_id).all()
    
    categories = []
    for ac in article_categories:
        category = Category.query.filter_by(category_id=ac.category_id).first()
        if category:
            categories.append({
                'category_id': category.category_id,
                'category_name': category.category_name
            })

    article_data = {
        'article_id': article.article_id,
        'title': article.title,
        'content': article.content,
        'created_at': article.created_at.isoformat(),
        'updated_at': article.updated_at.isoformat(),
        'categories': categories,
        'user': user_data
    }
    
    return jsonify(article_data), 200