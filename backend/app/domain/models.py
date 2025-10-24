from datetime import datetime
from app.extensions import db

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Course(db.Model, TimestampMixin):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    lesson_count = db.Column(db.Integer, nullable=False, default=1)
    has_certification = db.Column(db.Boolean, nullable=False, default=False)

    lessons = db.relationship("Lesson",
        backref="course",
        order_by="Lesson.index",
        cascade="all, delete-orphan")

class Lesson(db.Model, TimestampMixin):
    __tablename__ = "lessons"
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    index = db.Column(db.Integer, nullable=False)  # 1..N
    title = db.Column(db.String(255), nullable=False, default="")

    chapters = db.relationship("Chapter",
        backref="lesson",
        order_by="Chapter.index",
        cascade="all, delete-orphan")

    quiz = db.relationship("Quiz",
        backref="lesson",
        uselist=False,
        cascade="all, delete-orphan")

class Chapter(db.Model, TimestampMixin):
    __tablename__ = "chapters"
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    index = db.Column(db.Integer, nullable=False)  # 1..M
    title = db.Column(db.String(255), nullable=False, default="")
    html_content = db.Column(db.Text, nullable=False, default="")

# --- Quiz models ---
class Quiz(db.Model, TimestampMixin):
    __tablename__ = "quizzes"
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(255), nullable=False, default="Quiz")

    questions = db.relationship("Question", backref="quiz", cascade="all, delete-orphan", order_by="Question.index")

class Question(db.Model, TimestampMixin):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    index = db.Column(db.Integer, nullable=False)  # 1..K
    text = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False, default="single")  # single|multiple

    options = db.relationship("AnswerOption", backref="question", cascade="all, delete-orphan", order_by="AnswerOption.id")

class AnswerOption(db.Model, TimestampMixin):
    __tablename__ = "answer_options"
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)
