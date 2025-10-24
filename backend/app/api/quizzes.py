from flask import Blueprint, request, jsonify
from app.services import course_service

bp = Blueprint("quizzes", __name__, url_prefix="/api/quizzes")

@bp.post("/create-for-lesson")
def create_for_lesson():
    data = request.get_json(force=True) or {}
    lesson_id = int(data.get("lesson_id", 0))
    title = (data.get("title") or "Quiz").strip()
    try:
        qz = course_service.get_or_create_quiz_for_lesson(lesson_id, title)
        return jsonify({"id": qz.id, "lesson_id": qz.lesson_id, "title": qz.title}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.get("/by-lesson/<int:lesson_id>")
def by_lesson(lesson_id: int):
    qz = course_service.get_quiz_by_lesson(lesson_id)
    if not qz:
        return jsonify({"quiz": None})
    return jsonify({
        "id": qz.id,
        "lesson_id": qz.lesson_id,
        "title": qz.title,
        "questions": [{
            "id": qu.id,
            "index": qu.index,
            "text": qu.text,
            "type": qu.type,
            "options": [{
                "id": op.id, "text": op.text, "is_correct": op.is_correct
            } for op in qu.options]
        } for qu in qz.questions]
    })
