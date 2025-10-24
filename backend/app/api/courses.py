from flask import Blueprint, request, jsonify
from app.services import course_service

bp = Blueprint("courses", __name__, url_prefix="/api/courses")

@bp.post("")
def create():
    data = request.get_json(force=True) or {}
    try:
        course = course_service.create_course(
            title=data.get("title"),
            lesson_count=int(data.get("lesson_count", 1)),
            has_certification=bool(data.get("has_certification", False)),
        )
        return jsonify({"id": course.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.get("")
def list_():
    items = course_service.list_courses()
    return jsonify([{
        "id": c.id,
        "title": c.title,
        "lesson_count": c.lesson_count,
        "has_certification": c.has_certification,
        "created_at": c.created_at.isoformat(),
        "updated_at": c.updated_at.isoformat(),
    } for c in items])

@bp.get("/<int:course_id>")
def detail(course_id: int):
    c = course_service.get_course_detail(course_id)
    if not c:
        return jsonify({"error":"not found"}), 404
    return jsonify({
        "id": c.id,
        "title": c.title,
        "lesson_count": c.lesson_count,
        "has_certification": c.has_certification,
        "lessons": [{
            "id": l.id,
            "index": l.index,
            "title": l.title,
            "chapters": [{
                "id": ch.id,
                "index": ch.index,
                "title": ch.title
            } for ch in l.chapters]
        } for l in c.lessons]
    })

@bp.patch("/<int:course_id>")
def patch(course_id: int):
    data = request.get_json(force=True) or {}
    try:
        c = course_service.update_course(course_id,
                                         title=data.get("title") if "title" in data else None,
                                         has_certification=data.get("has_certification") if "has_certification" in data else None)
        if not c:
            return jsonify({"error":"not found"}), 404
        return jsonify({"id": c.id, "title": c.title, "has_certification": c.has_certification})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.delete("/<int:course_id>")
def delete(course_id: int):
    ok = course_service.delete_course(course_id)
    if not ok:
        return jsonify({"error":"not found"}), 404
    return ("", 204)
