from flask import Blueprint, jsonify, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import FollowEvent, TextMessage, TextSendMessage
import redis
from project.models import db, User  # あなたのUserモデルに応じて変更
import os

line_bp = Blueprint("line_webhook", __name__)

