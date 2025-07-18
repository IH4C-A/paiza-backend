from datetime import datetime
from flask_login import UserMixin
import uuid
from project import db

# Userテーブル✅
class User(db.Model, UserMixin):
    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    username = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(255), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    seibetu = db.Column(db.String(10), nullable=True)  # 性別
    address = db.Column(db.String(255), nullable=True)
    employment_status = db.Column(db.String(50), nullable=True)  # 雇用形態
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    line_login_user_id = db.Column(db.String(64), unique=True, nullable=True)  # LINEログインのsub
    line_bot_user_id   = db.Column(db.String(64), unique=True, nullable=True)  # Bot通知用

    
    def get_id(self):
        return str(self.user_id)

# categoryテーブル
class Category(db.Model):
    category_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    category_name = db.Column(db.String(255), unique=True, nullable=False)
    category_code = db.Column(db.String(255), nullable=False)  

# User_categoryテーブル✅
class User_category(db.Model):
    user_category_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    category_id = db.Column(db.String(36), db.ForeignKey('category.category_id'), nullable=False)
    
    user = db.relationship('User', backref='user_categories', lazy=True)
    category = db.relationship('Category', backref='user_categories', lazy=True)

# School_infoテーブル✅
class School_info(db.Model):
    school_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    school_name = db.Column(db.String(255), nullable=False)
    school_type = db.Column(db.String(50), nullable=False)  # 学校種別
    study_line = db.Column(db.String(255), nullable=False)
    academic_department = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='school_info', lazy=True)

# Rankテーブル
class Rank(db.Model):
    rank_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    rank_name = db.Column(db.String(50), nullable=False)  # ランク名

# User_rankテーブル✅
class User_rank(db.Model):
    user_rank_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    rank_id = db.Column(db.String(36), db.ForeignKey('rank.rank_id'), nullable=False)
    rank_code = db.Column(db.String(255), nullable=False)
    
    user = db.relationship('User', backref='user_ranks', lazy=True)
    rank = db.relationship('Rank', backref='user_ranks', lazy=True)

# Problemテーブル✅
class Problem(db.Model):
    problem_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    problem_title = db.Column(db.String(255),nullable=False)
    problem_text = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.String(36), db.ForeignKey('category.category_id'), nullable=False)
    rank_id = db.Column(db.String(36), db.ForeignKey('rank.rank_id'), nullable=False)
    
    category = db.relationship('Category', backref='problems', lazy=True)
    rank = db.relationship('Rank', backref='problems', lazy=True)

class Submission(db.Model):
    __tablename__ = 'submission'

    submission_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    problem_id = db.Column(db.String(36), db.ForeignKey('problem.problem_id'), nullable=False)
    code_text = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(20), nullable=False)
    passed = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='submissions', lazy=True)
    problem = db.relationship('Problem', backref='submissions', lazy=True)

class TestCase(db.Model):
    __tablename__ = 'test_case'

    test_case_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    problem_id = db.Column(db.String(36), db.ForeignKey('problem.problem_id'), nullable=False)
    input_text = db.Column(db.Text, nullable=False)
    expected_output = db.Column(db.Text, nullable=False)
    is_public = db.Column(db.Boolean, default=False)

    problem = db.relationship('Problem', backref='test_cases', lazy=True)

# Answerテーブル✅
class Answer(db.Model):
    answer_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    problem_id = db.Column(db.String(36), db.ForeignKey('problem.problem_id'), nullable=False)
    answer_text = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=True)
    
    problem = db.relationship('Problem', backref='answers', lazy=True)

# Mentorshipテーブル✅
class Mentorship(db.Model):
    mentorship_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    mentor_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    mentee_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    mentor = db.relationship('User', foreign_keys=[mentor_id], backref='mentorships_as_mentor', lazy=True)
    mentee = db.relationship('User', foreign_keys=[mentee_id], backref='mentorships_as_mentee', lazy=True)

class MentorshipRequest(db.Model):
    request_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    mentee_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    mentor_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending / approved / rejected
    message = db.Column(db.Text, nullable=True)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)

    mentee = db.relationship('User', foreign_keys=[mentee_id])
    mentor = db.relationship('User', foreign_keys=[mentor_id])

# Plantテーブル✅
class Plant(db.Model):
    plant_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    plant_name = db.Column(db.String(255), nullable=False)
    growth_stage = db.Column(db.String(255), nullable=False)
    mood = db.Column(db.String(50), nullable=False)  # 植物の種類
    color = db.Column(db.String(50), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    motivation_style = db.Column(db.String(50), nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='plants', lazy=True)

# growth_milestonesテーブル
class GrowthMilestone(db.Model):
    milestone_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    plant_id = db.Column(db.String(36), db.ForeignKey('plant.plant_id'), nullable=False)
    milestone = db.Column(db.Integer, nullable=False)  # 成長段階のマイルストーン
    level = db.Column(db.Integer, nullable=True)  # レベル
    achieved_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    plant = db.relationship('Plant', backref='growth_milestones', lazy=True)

# growth_milestone_logsテーブル
class GrowthMilestoneLog(db.Model):
    log_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    milestone_id = db.Column(db.String(36), db.ForeignKey('growth_milestone.milestone_id'), nullable=False)
    log_message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    milestone = db.relationship('GrowthMilestone', backref='logs', lazy=True)

# GroupChatテーブル✅
class GroupChat(db.Model):
    __tablename__ = 'group_chat'
    group_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    group_name = db.Column(db.String(255),nullable=False)
    group_description = db.Column(db.Text, nullable=True)
    group_image = db.Column(db.String(255), nullable=True)
    create_at = db.Column(db.DateTime, default=datetime.utcnow)
    create_by = db.Column(db.String(36), db.ForeignKey('user.user_id'))

# GroupMemberテーブル✅
class GroupMember(db.Model):
    group_member_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    group_id = db.Column(db.String(36), db.ForeignKey('group_chat.group_id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)

# chatsテーブル✅
class Chats(db.Model):
    chat_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    message = db.Column(db.String(255), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    type = db.Column(db.String(255), nullable=True)
    send_user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    receiver_user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=True)
    group_id = db.Column(db.String(36), db.ForeignKey('group_chat.group_id'), nullable=True)
    chat_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    # relation
    sender = db.relationship('User', foreign_keys=[send_user_id])
    receiver = db.relationship('User', foreign_keys=[receiver_user_id])
    group = db.relationship('GroupChat', foreign_keys=[group_id])

# Boardテーブル
class Board(db.Model):
    board_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False)  # ステータス
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='boards', lazy=True)

# boardcategoryテーブル
class Board_Category(db.Model):
    board_category_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    category_id = db.Column(db.String(36), db.ForeignKey('category.category_id'), nullable=False)
    board_id = db.Column(db.String(36), db.ForeignKey('board.board_id'), nullable=False)

    category = db.relationship('Category', backref='board_categories', lazy=True)
    board = db.relationship('Board', backref='board_categories', lazy=True)

# commentテーブル
class Comment(db.Model):
    comment_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    board_id = db.Column(db.String(36), db.ForeignKey('board.board_id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_answered = db.Column(db.Boolean, default=False)  # 回答済みフラグ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    board = db.relationship('Board', backref='comments', lazy=True)
    user = db.relationship('User', backref='comments', lazy=True)

# coursesテーブル✅
class Courses(db.Model):
    course_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    course_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category_id = db.Column(db.String(36), db.ForeignKey('category.category_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category = db.relationship('Category', backref='courses', lazy=True)

# Course_progressテーブル✅
class CourseProgress(db.Model):
    progress_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    course_id = db.Column(db.String(36), db.ForeignKey('courses.course_id'), nullable=False)
    progress_percentage = db.Column(db.Integer, nullable=False)  # 進捗率
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='course_progress', lazy=True)
    course = db.relationship('Courses', backref='course_progress', lazy=True)

# study_logsテーブル✅
class StudyLogs(db.Model):
    log_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    course_id = db.Column(db.String(36), db.ForeignKey('courses.course_id'), nullable=False)
    study_time = db.Column(db.Integer, nullable=False)  # 学習時間（分）
    study_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='study_logs', lazy=True)
    course = db.relationship('Courses', backref='study_logs', lazy=True)

# Notificationテーブル✅
class Notification(db.Model):
    notification_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)  # 未読フラグ
    type = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    detail = db.Column(db.String(255), nullable=False)
    priority = db.Column(db.String(255), nullable=False)
    actionurl = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='notifications', lazy=True)

# Articleテーブル✅
class Article(db.Model):
    article_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='articles', lazy=True)

# ArticleCategoryテーブル✅
class ArticleCategory(db.Model):
    article_category_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    article_id = db.Column(db.String(36), db.ForeignKey('article.article_id'), nullable=False)
    category_id = db.Column(db.String(36), db.ForeignKey('category.category_id'), nullable=False)
    
    article = db.relationship('Article', backref='article_categories', lazy=True)
    category = db.relationship('Category', backref='article_categories', lazy=True)

# ArticleLikesテーブル
class ArticleLikes(db.Model):
    like_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    article_id = db.Column(db.String(36), db.ForeignKey('article.article_id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    
    article = db.relationship('Article', backref='likes', lazy=True)
    user = db.relationship('User', backref='liked_articles', lazy=True)  # ユーザーがいいねした記事

class MentorshipSchedule(db.Model):
    schedule_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    mentorship_id = db.Column(db.String(36), db.ForeignKey('mentorship.mentorship_id'), nullable=True)
    group_id = db.Column(db.String(36), db.ForeignKey('group_chat.group_id'), nullable=True)  # グループチャットのID
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum('scheduled', 'completed', 'canceled', name='mentorship_status'), default='scheduled', nullable=False)
    topic = db.Column(db.String(255))  # フリーテキストも可能
    description = db.Column(db.Text)
    meeting_link = db.Column(db.String(255))  # オンラインミーティングのリンクなど
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cancel_reason = db.Column(db.Text)

    group = db.relationship('GroupChat', backref='mentorship_schedules', uselist=False)
    mentorship = db.relationship('Mentorship', backref='schedule', uselist=False)

class MentorshipNote(db.Model):
    note_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    mentorship_id = db.Column(db.String(36), db.ForeignKey('mentorship.mentorship_id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)

    type = db.Column(db.Enum('preparation', 'summary', name='note_type'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    mentorship = db.relationship('Mentorship', backref='notes')
    user = db.relationship('User', backref='mentorship_notes')

class MentorshipFeedback(db.Model):
    feedback_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    mentorship_id = db.Column(db.String(36), db.ForeignKey('mentorship.mentorship_id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)

    rating = db.Column(db.Integer, nullable=False)  # 1〜5段階
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    mentorship = db.relationship('Mentorship', backref='feedbacks')
    user = db.relationship('User', backref='given_feedbacks')
