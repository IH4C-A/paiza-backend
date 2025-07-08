from datetime import datetime
import uuid
from project.models import Notification
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
    
    try:
        line_message = f"🔔 {title}\n{message}\n優先度: {priority}"
        send_line_notification(line_message)
    except Exception as e:
        print(f"LINE通知エラー: {e}")
