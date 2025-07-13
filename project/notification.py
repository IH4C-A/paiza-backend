from datetime import datetime
from project.models import Notification, User  # Userを追加
from project import db
from project.linebot import send_line_notification


def create_notification(
    user_id,
    title,
    message,
    detail,
    type,
    priority,
    actionurl
):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        detail=detail,
        type=type,
        priority=priority,
        actionurl=actionurl,
        is_read=False,
        created_at=datetime.utcnow()
    )
    db.session.add(notification)
    db.session.commit()

    # ✅ user情報を取得して、line_bot_user_idがあるか確認
    try:
        user = User.query.get(user_id)
        if user and user.line_bot_user_id:
            line_message = f"🔔 {title}\n{message}\n優先度: {priority}"
            send_line_notification(line_message, user.line_bot_user_id)
    except Exception as e:
        print(f"LINE通知エラー: {e}")
