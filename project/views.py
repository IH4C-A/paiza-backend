from flask import request, jsonify, Blueprint
import os


bp = Blueprint('main', __name__)

# Hello World
@bp.route('/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello, World!"})