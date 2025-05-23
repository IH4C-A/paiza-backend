from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from project.models import Comment
from flask_login import login_user
from project import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

comment_bp = Blueprint('commnt', __name__)

