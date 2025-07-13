from flask import Blueprint, jsonify, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import FollowEvent, TextMessage, TextSendMessage
from project.models import db, User  # あなたのUserモデルに応じて変更
import os

line_bp = Blueprint("line_webhook", __name__)

from linebot import LineBotApi, WebhookHandler

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_SECRET"))


@line_bp.route("/line/webhook", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_user_id = event.source.user_id

    # 既にログインしているユーザー（line_login_user_id）と紐付け
    user = User.query.filter_by(line_login_user_id=line_bot_user_id).first()
    if user:
        user.line_bot_user_id = line_bot_user_id  # 友達追加されたことを記録
        db.session.commit()

    # 友だち追加時の初期メッセージを送信
    welcome_text = "友だち追加ありがとうございます！\n通知連携が完了しました。"
    try:
        line_bot_api.push_message(line_bot_user_id, TextSendMessage(text=welcome_text))
    except Exception as e:
        # エラーログ出力など必要に応じて
        print(f"Error sending welcome message: {e}")

