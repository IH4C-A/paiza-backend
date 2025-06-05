from datetime import datetime
from project.models import Notification
from project import db

def create_notification(user_id, notification):
    notification_comp = Notification(user_id=user_id,notification=notification)
    db.session.add(notification_comp)