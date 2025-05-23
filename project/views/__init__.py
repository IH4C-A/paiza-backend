from .user_views import user_bp
from .answer_views import answer_bp
from .chats_views import chats_bp
from .problem_views import problem_bp
from .comment_views import comment_bp

def register_blueprints(app):
    app.register_blueprint(user_bp)
    app.register_blueprint(chats_bp)
    app.register_blueprint(answer_bp)
    app.register_blueprint(problem_bp)
    app.register_blueprint(comment_bp)
    
