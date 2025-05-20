from .user_views import user_bp
from .answer_views import answer_bp

def register_blueprints(app):
    app.register_blueprint(user_bp)

def register_blueprints(app):
    app.register_blueprint(answer_bp)