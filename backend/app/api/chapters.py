from flask import Blueprint, request, jsonify
from app.services import course_service

bp = Blueprint("chapters", __name__, url_prefix="/api/chapters")

@bp.post("/add")
def add():
    data = request.get_json(force=True) or {}
    try:
        ch = course_service.add_chapter(
            lesson_id=int(data.get("lesson_id", 0)),
            title=(data.get("title") or "").strip(),
            html_content=data.get("html_content") or "",
        )
        return jsonify({"id": ch.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.get("/<int:chapter_id>")
def get_one(chapter_id: int):
    ch = course_service.get_chapter(chapter_id)
    if not ch:
        return jsonify({"error": "not found"}), 404
    return jsonify({
        "id": ch.id,
        "lesson_id": ch.lesson_id,
        "index": ch.index,
        "title": ch.title,
        "html_content": ch.html_content,
    })

@bp.patch("/<int:chapter_id>")
def patch(chapter_id: int):
    data = request.get_json(force=True) or {}
    try:
        ch = course_service.update_chapter(
            chapter_id,
            title=data.get("title") if "title" in data else None,
            html_content=data.get("html_content") if "html_content" in data else None,
        )
        if not ch:
            return jsonify({"error":"not found"}), 404
        return jsonify({"id": ch.id, "title": ch.title})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.delete("/<int:chapter_id>")
def delete(chapter_id: int):
    ok = course_service.delete_chapter(chapter_id)
    if not ok:
        return jsonify({"error":"not found"}), 404
    return ("", 204)
