from datetime import datetime
import uuid
from project.models import Notification
from project import db

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
