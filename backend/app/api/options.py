from flask import Blueprint, request, jsonify
from app.services import course_service

bp = Blueprint("options", __name__, url_prefix="/api/options")

@bp.post("/add")
def add():
    data = request.get_json(force=True) or {}
    try:
        o = course_service.add_option(
            question_id=int(data.get("question_id", 0)),
            text=data.get("text"),
            is_correct=bool(data.get("is_correct", False)),
        )
        return jsonify({"id": o.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.patch("/<int:option_id>")
def patch(option_id: int):
    data = request.get_json(force=True) or {}
    try:
        o = course_service.update_option(
            option_id,
            text=data.get("text") if "text" in data else None,
            is_correct=data.get("is_correct") if "is_correct" in data else None,
        )
        if not o: return jsonify({"error":"not found"}), 404
        return jsonify({"id": o.id})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.delete("/<int:option_id>")
def delete(option_id: int):
    ok = course_service.delete_option(option_id)
    if not ok: return jsonify({"error":"not found"}), 404
    return ("", 204)
