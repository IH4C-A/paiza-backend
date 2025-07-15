import os
import requests
from dotenv import load_dotenv

load_dotenv()

FRONTEND_BASE_URL = "https://paiza-nurture.inrigsnet.com"

def send_line_flex_notification(title: str, message: str, line_user_id: str, actionurl: str):
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

    # ✅ actionurl が相対パスなら、完全URLに変換
    if actionurl.startswith("/"):
        actionurl = FRONTEND_BASE_URL + actionurl

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "to": line_user_id,
        "messages": [
            {
                "type": "flex",
                "altText": "新しい通知があります",
                "contents": {
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"🔔 {title}",
                                "weight": "bold",
                                "size": "lg",
                                "wrap": True
                            },
                            {
                                "type": "text",
                                "text": message,
                                "wrap": True,
                                "margin": "md"
                            }
                        ]
                    },
                    "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "button",
                                "style": "link",
                                "height": "sm",
                                "action": {
                                    "type": "uri",
                                    "label": "🔗 詳細を見る",
                                    "uri": actionurl
                                }
                            }
                        ],
                        "flex": 0
                    }
                }
            }
        ]
    }

    res = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)
    print(f"[Flex] LINE通知: {res.status_code}")
    print(res.text)

