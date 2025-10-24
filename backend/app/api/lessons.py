from flask import Blueprint, request, jsonify
from app.services import course_service

bp = Blueprint("lessons", __name__, url_prefix="/api/lessons")

@bp.patch("/<int:lesson_id>")
def patch(lesson_id: int):
    data = request.get_json(force=True) or {}
    try:
        l = course_service.update_lesson(
            lesson_id,
            title=data.get("title") if "title" in data else None,
        )
        if not l:
            return jsonify({"error":"not found"}), 404
        return jsonify({"id": l.id, "title": l.title})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
