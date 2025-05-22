from .user_views import user_bp
from .chats_views import chats_bp

def register_blueprints(app):
    app.register_blueprint(user_bp)
    app.register_blueprint(chats_bp)