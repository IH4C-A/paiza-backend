import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_line_notification(message: str, line_user_id: str):
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "to": line_user_id,
        "messages": [{"type": "text", "text": message}]
    }

    res = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)
    print(f"LINE通知: {res.status_code}")
    print(res.text)
