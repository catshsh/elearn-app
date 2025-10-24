from flask import Blueprint, send_file, abort
from io import BytesIO
from app.extensions import db
from app.domain.models import Course
from app.scorm.builder import build_scorm_zip

bp = Blueprint("export", __name__, url_prefix="/api/export")

@bp.get("/scorm/<int:course_id>")
def export_scorm(course_id: int):
    course = Course.query.get(course_id)
    if not course:
        abort(404)
    buf: BytesIO = build_scorm_zip(course)
    filename = f"course-{course_id}-scorm.zip"
    return send_file(buf, mimetype="application/zip", as_attachment=True, download_name=filename)
