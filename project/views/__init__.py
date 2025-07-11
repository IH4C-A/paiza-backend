from .user_views import user_bp
from .answer_views import answer_bp
from .chats_views import chats_bp
from .problem_views import problem_bp
from .comment_views import comment_bp
from .groupchat_views import groupchat_bp
from .Plant_views import Plant_bp
from .School_info_views import School_info_bp
from .user_category_views import user_category_bp
from .user_rank_views import user_rank_bp
from .mentorship_views import mentorship_bp
from .courses_views import courses_bp
from .courseprogress_views import courseprogress_bp
from .studylogs_views import studylogs_bp
from .notification_views import notification_bp
from .article_views import article_bp
from .articlecategory_views import articlecategory_bp
from .articlelikes_views import articlelikes_bp
from .category_views import category_bp
from .rank_views import rank_bp
from .Board_views import Board_bp
from .mentor_schedule_views import mentor_schedule_bp
from .mentor_note_views import mentor_note_bp
from .mentor_feedback_views import mentor_feedback_bp
from .testcase_views import test_case_api
from .submission_views import submission_api
from .gemini_views import gemini
from .line_views import line_bp

def register_blueprints(app):
    app.register_blueprint(user_bp)
    app.register_blueprint(chats_bp)
    app.register_blueprint(answer_bp)
    app.register_blueprint(problem_bp)
    app.register_blueprint(comment_bp)
    app.register_blueprint(groupchat_bp)
    app.register_blueprint(Plant_bp)
    app.register_blueprint(School_info_bp)
    app.register_blueprint(user_category_bp)
    app.register_blueprint(user_rank_bp)
    app.register_blueprint(mentorship_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(courseprogress_bp)
    app.register_blueprint(studylogs_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(article_bp)
    app.register_blueprint(articlecategory_bp)
    app.register_blueprint(articlelikes_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(rank_bp)
    app.register_blueprint(Board_bp)
    app.register_blueprint(mentor_schedule_bp)
    app.register_blueprint(mentor_note_bp)
    app.register_blueprint(mentor_feedback_bp)
    app.register_blueprint(test_case_api)
    app.register_blueprint(submission_api)
    app.register_blueprint(gemini)
    app.register_blueprint(line_bp)

