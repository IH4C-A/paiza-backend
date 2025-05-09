from flask import request, jsonify, Blueprint
import os


bp = Blueprint('main', __name__)

# Hello World
@bp.route('/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello, World!"})

# /route
@bp.route('/', methods=['GET'])
def index():
    print("hello")
    return jsonify({"message": "Welcome to the Flask API!"})