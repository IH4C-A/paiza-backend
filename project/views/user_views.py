from flask import redirect, request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
import requests
from project.models import Mentorship, Rank, User, User_rank
from flask_login import login_user
from project import db
from project.chat_response import calculate_average_dm_response_time, get_average_mentor_rating
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from jose import jwt

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = []
    for user in users:
        response = calculate_average_dm_response_time(user.user_id)
        average_rating = get_average_mentor_rating(user.user_id)
    # ランク情報の取得
        user_ranks = []
        for ur in user.user_ranks:
            user_ranks.append({
                'user_rank_id': ur.user_rank_id,
                'rank_id': ur.rank_id,
                'rank_name': ur.rank.rank_name,
                'rank_code': ur.rank_code
            })
        
        user_category = []
        for uc in user.user_categories:
            user_category.append({
                'user_category_id': uc.user_category_id,
                'category_id': uc.category_id,
                'category_name': uc.category.category_name,
                'category_code': uc.category.category_code
            })

        user_data = {
            'user_id': user.user_id,
            'password': user.password,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'profile_image': user.profile_image,
            'age': user.age,
            'seibetu': user.seibetu,
            'address': user.address,
            'employment_status': user.employment_status,
            'created_at': user.created_at.isoformat(),
            'ranks': user_ranks,
            'categories': user_category,
            'response_time': response if response is not None else "No DM history",
            'average_rating': average_rating if average_rating is not None else 0
        }
        user_list.append(user_data)
    return jsonify(user_list), 200


@user_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    
    response = calculate_average_dm_response_time(user.user_id)
    average_rating = get_average_mentor_rating(user.user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404


    mentees_count = Mentorship.query.filter_by(mentor_id=user.user_id).count()
    # ランク情報の取得
    user_ranks = []
    for ur in user.user_ranks:
        user_ranks.append({
            'user_rank_id': ur.user_rank_id,
            'rank_id': ur.rank_id,
            'rank_name': ur.rank.rank_name,
            'rank_code': ur.rank_code
        })
        
    user_category = []
    for uc in user.user_categories:
        user_category.append({
            'user_category_id': uc.user_category_id,
            'category_id': uc.category_id,
            'category_name': uc.category.category_name,
            'category_code': uc.category.category_code
        })

    user_data = {
        'user_id': user.user_id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'profile_image': user.profile_image,
        'age': user.age,
        'seibetu': user.seibetu,
        'address': user.address,
        'employment_status': user.employment_status,
        'created_at': user.created_at.isoformat(),
        'mentees_count': mentees_count,
        'ranks': user_ranks,
        'categories': user_category,
        'response_time': response if response is not None else "No DM history",
        'average_rating': average_rating if average_rating is not None else 0
    }
    return jsonify(user_data), 200

# 画像取得
@user_bp.route('/prof_image/<filename>', methods=['GET'])
def get_profile_image(filename):
    # 画像のパスを指定
    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    # 画像が存在するか確認
    if os.path.exists(image_path):
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
    else:
        return jsonify({"error": "Image not found."}), 404

# User登録
@user_bp.route('/user', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    profile_image = data.get('profile_image')
    age = data.get('age')
    seibetu = data.get('seibetu')
    address = data.get('address')
    employment_status = data.get('employment_status')
    line_login_user_id=data.get("line_login_user_id"),

    if  not password or not email:
        return jsonify({"error": "Username, password, and email are required."}), 400
    # 画像がアップロードされていない場合のデフォルト設定
    if profile_image:
        prof_image_filename = secure_filename(profile_image.filename)
        profile_image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], prof_image_filename))
    else:
        prof_image_filename = None  # 画像がない場合はNoneを設定
    
    hashed_password = generate_password_hash(password, method='sha256')

    new_user = User(
        username=username,
        password=hashed_password,
        email=email,
        first_name=first_name,
        last_name=last_name,
        profile_image=profile_image,
        age=age,
        seibetu=seibetu,
        address=address,
        employment_status=employment_status,
        line_login_user_id=line_login_user_id
    )

    db.session.add(new_user)
    db.session.commit()
    
    rank = Rank.query.filter_by(rank_name='D').first()
    # User_rankの登録
    new_user_rank = User_rank(
        user_id=new_user.user_id,
        rank_id=rank.rank_id,  # デフォルトのランクIDを1とする
        rank_code='student',
    )
    db.session.add(new_user_rank)
    db.session.commit()

    return jsonify({
        'user_id': new_user.user_id,
        'username': new_user.username,
        'email': new_user.email,
        'first_name': new_user.first_name,
        'last_name': new_user.last_name,
        'profile_image': new_user.profile_image,
        'age': new_user.age,
        'seibetu': new_user.seibetu,
        'address': new_user.address,
        'employment_status': new_user.employment_status}), 201

# Userアップデート
@user_bp.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    data = request.get_json()
    user.username = data.get('username', user.username)
    user.password = generate_password_hash(data.get('password', user.password), method='sha256')
    user.email = data.get('email', user.email)
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.profile_image = data.get('profile_image', user.profile_image)
    user.age = data.get('age', user.age)
    user.seibetu = data.get('seibetu', user.seibetu)
    user.address = data.get('address', user.address)
    user.employment_status = data.get('employment_status', user.employment_status)

    db.session.commit()

    return jsonify({"message": "User updated successfully!"})

# User削除
@user_bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted successfully!"})

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    line_user_id = data.get('line_user_id')  # LINEログイン用

    # --- LINEログイン処理 ---
    if line_user_id:
        user = User.query.filter_by(line_login_user_id=line_user_id).first()
        if not user:
            return jsonify({'error': 'LINEユーザーが見つかりません'}), 404

        access_token = create_access_token(identity=user.user_id)
        return jsonify({'token': access_token}), 200

    # --- メール＆パスワード ログイン処理 ---
    if not email or not password:
        return jsonify({"error": "メールアドレスとパスワードは必須です"}), 400

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.user_id)
        return jsonify({'token': access_token}), 200
    else:
        return jsonify({'error': 'ログインに失敗しました'}), 400

@user_bp.route('/login_user', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    response = calculate_average_dm_response_time(current_user_id)
    average_rating = get_average_mentor_rating(current_user_id)
    if not current_user:
        return jsonify({"error": "User not found."}), 404

    # ランク情報の取得
    user_ranks = []
    for ur in current_user.user_ranks:
        user_ranks.append({
            'user_rank_id': ur.user_rank_id,
            'rank_id': ur.rank_id,
            'rank_name': ur.rank.rank_name,
            'rank_code': ur.rank_code
        })
        
    user_category = []
    for uc in current_user.user_categories:
        user_category.append({
            'user_category_id': uc.user_category_id,
            'category_id': uc.category_id,
            'category_name': uc.category.category_name,
            'category_code': uc.category.category_code
        })

    user_data = {
        'user_id': current_user.user_id,
        'username': current_user.username,
        'email': current_user.email,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'profile_image': current_user.profile_image,
        'age': current_user.age,
        'seibetu': current_user.seibetu,
        'address': current_user.address,
        'employment_status': current_user.employment_status,
        'ranks': user_ranks,
        'categories': user_category,
        'response_time': response if response is not None else "No DM history",
        'average_rating': average_rating if average_rating is not None else 0
    }
    return jsonify(user_data), 200




# Hello World
@user_bp.route('/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello, World!"})

# /route
@user_bp.route('/', methods=['GET'])
def index():
    print("hello")
    return jsonify({"message": "Welcome to the Flask API!"})

@user_bp.route("/api/line/callback")
def line_callback():
    code = request.args.get("code")
    redirect_uri = "https://paiza-nurture-api.inrigsnet.com/api/line/callback"

    # アクセストークン取得
    token_res = requests.post(
        "https://api.line.me/oauth2/v2.1/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": os.getenv("LINE_LOGIN_CHANNEL_ID"),
            "client_secret": os.getenv("LINE_LOGIN_CHANNEL_SECRET"),
        },
    )
    token_data = token_res.json()
    id_token = token_data.get("id_token")

    if not id_token:
        # エラーハンドリング
        return "Invalid token response", 400

    decoded = jwt.decode(
        id_token,
        os.getenv("LINE_LOGIN_CHANNEL_SECRET"),
        algorithms=["HS256"],
        audience=os.getenv("LINE_LOGIN_CHANNEL_ID"),
    )

    line_user_id = decoded["sub"]

    # DBからユーザー検索
    user = User.query.filter_by(line_login_user_id=line_user_id).first()

    if user:
        # ログイン処理にリダイレクト（トークン発行やセッション設定など）
        # 例: JWT発行してフロントに渡すURLへリダイレクト
        # ここはあなたのログイン後のURLに置き換えてください
        login_redirect_url = f"https://paiza-nurture.inrigsnet.com/auth/signin?line_user_id={line_user_id}"
        return redirect(login_redirect_url)

    else:
        # 未登録なら登録ページにリダイレクト
        signup_redirect_url = f"https://paiza-nurture.inrigsnet.com/auth/signup?line_user_id={line_user_id}"
        return redirect(signup_redirect_url)
