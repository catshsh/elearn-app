from flask import Blueprint, request, jsonify
from app.services import course_service

bp = Blueprint("questions", __name__, url_prefix="/api/questions")

@bp.post("/add")
def add():
    data = request.get_json(force=True) or {}
    try:
        q = course_service.add_question(
            quiz_id=int(data.get("quiz_id", 0)),
            text=data.get("text"),
            qtype=data.get("type", "single"),
        )
        return jsonify({"id": q.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.patch("/<int:question_id>")
def patch(question_id: int):
    data = request.get_json(force=True) or {}
    try:
        q = course_service.update_question(
            question_id,
            text=data.get("text") if "text" in data else None,
            qtype=data.get("type") if "type" in data else None,
        )
        if not q: return jsonify({"error":"not found"}), 404
        return jsonify({"id": q.id})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.delete("/<int:question_id>")
def delete(question_id: int):
    ok = course_service.delete_question(question_id)
    if not ok: return jsonify({"error":"not found"}), 404
    return ("", 204)
