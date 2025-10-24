from flask import Flask, jsonify
from .config import load_config
from .extensions import db, migrate, cors

from .domain import models  # noqa: F401
from .api.courses import bp as courses_bp
from .api.chapters import bp as chapters_bp
from .api.lessons import bp as lessons_bp
from .api.quizzes import bp as quizzes_bp
from .api.questions import bp as questions_bp
from .api.options import bp as options_bp
from .api.export import bp as export_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(load_config())

    cors(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    migrate.init_app(app, db)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    app.register_blueprint(courses_bp)
    app.register_blueprint(chapters_bp)
    app.register_blueprint(lessons_bp)
    app.register_blueprint(quizzes_bp)
    app.register_blueprint(questions_bp)
    app.register_blueprint(options_bp)
    app.register_blueprint(export_bp)
    return app
