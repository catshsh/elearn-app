from app.extensions import db
from app.domain.models import Course, Lesson, Chapter, Quiz, Question, AnswerOption

# --- Courses / Lessons / Chapters (déjà connus) ---
def create_course(title: str, lesson_count: int, has_certification: bool) -> Course:
    title = (title or "").strip()
    if not title:
        raise ValueError("Le titre est requis.")
    if lesson_count < 1 or lesson_count > 100:
        raise ValueError("lesson_count doit être entre 1 et 100.")
    c = Course(title=title, lesson_count=lesson_count, has_certification=has_certification)
    db.session.add(c); db.session.flush()
    for i in range(1, lesson_count + 1):
        db.session.add(Lesson(course_id=c.id, index=i, title=f"Leçon {i}"))
    db.session.commit()
    return c

def list_courses():
    return Course.query.order_by(Course.created_at.desc()).all()

def get_course_detail(course_id: int):
    return Course.query.filter_by(id=course_id).first()

def add_chapter(lesson_id: int, title: str, html_content: str):
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        raise ValueError("Lesson introuvable.")
    next_index = (lesson.chapters[-1].index + 1) if lesson.chapters else 1
    ch = Chapter(lesson_id=lesson_id, index=next_index, title=(title or "").strip(), html_content=html_content or "")
    db.session.add(ch); db.session.commit()
    return ch

def get_chapter(chapter_id: int):
    return Chapter.query.get(chapter_id)

def update_course(course_id: int, *, title=None, has_certification=None):
    c = Course.query.get(course_id)
    if not c: return None
    changed = False
    if title is not None:
        t = (title or "").strip()
        if not t: raise ValueError("Le titre est requis.")
        if c.title != t: c.title = t; changed = True
    if has_certification is not None and c.has_certification != bool(has_certification):
        c.has_certification = bool(has_certification); changed = True
    if changed: db.session.commit()
    return c

def update_lesson(lesson_id: int, *, title=None):
    l = Lesson.query.get(lesson_id)
    if not l: return None
    changed = False
    if title is not None:
        t = (title or "").strip()
        if not t: raise ValueError("Titre de la leçon requis.")
        if l.title != t: l.title = t; changed = True
    if changed: db.session.commit()
    return l

def update_chapter(chapter_id: int, *, title=None, html_content=None):
    ch = Chapter.query.get(chapter_id)
    if not ch: return None
    changed = False
    if title is not None:
        t = (title or "").strip()
        if not t: raise ValueError("Titre du chapitre requis.")
        if ch.title != t: ch.title = t; changed = True
    if html_content is not None and ch.html_content != html_content:
        ch.html_content = html_content; changed = True
    if changed: db.session.commit()
    return ch

def delete_course(course_id: int) -> bool:
    c = Course.query.get(course_id)
    if not c: return False
    db.session.delete(c); db.session.commit()
    return True

def delete_chapter(chapter_id: int) -> bool:
    ch = Chapter.query.get(chapter_id)
    if not ch: return False
    db.session.delete(ch); db.session.commit()
    return True

# --- Quiz / Questions / Options ---
def get_or_create_quiz_for_lesson(lesson_id: int, title: str = "Quiz"):
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        raise ValueError("Lesson introuvable.")
    if lesson.quiz:
        return lesson.quiz
    qz = Quiz(lesson_id=lesson_id, title=title)
    db.session.add(qz); db.session.commit()
    return qz

def get_quiz_by_lesson(lesson_id: int):
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return None
    return lesson.quiz

def add_question(quiz_id: int, text: str, qtype: str = "single"):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        raise ValueError("Quiz introuvable.")
    if (qtype or "single") not in {"single","multiple"}:
        raise ValueError("Type de question invalide.")
    next_index = (quiz.questions[-1].index + 1) if quiz.questions else 1
    q = Question(quiz_id=quiz_id, index=next_index, text=(text or "").strip(), type=qtype or "single")
    if not q.text:
        raise ValueError("Le texte de la question est requis.")
    db.session.add(q); db.session.commit()
    return q

def update_question(question_id: int, *, text=None, qtype=None):
    q = Question.query.get(question_id)
    if not q: return None
    changed = False
    if text is not None:
        t = (text or "").strip()
        if not t: raise ValueError("Texte de question requis.")
        if q.text != t: q.text = t; changed = True
    if qtype is not None:
        if qtype not in {"single","multiple"}:
            raise ValueError("Type invalide.")
        if q.type != qtype: q.type = qtype; changed = True
    if changed: db.session.commit()
    return q

def delete_question(question_id: int) -> bool:
    q = Question.query.get(question_id)
    if not q: return False
    db.session.delete(q); db.session.commit()
    return True

def add_option(question_id: int, text: str, is_correct: bool = False):
    q = Question.query.get(question_id)
    if not q:
        raise ValueError("Question introuvable.")
    opt = AnswerOption(question_id=question_id, text=(text or "").strip(), is_correct=bool(is_correct))
    if not opt.text:
        raise ValueError("Texte de réponse requis.")
    db.session.add(opt); db.session.commit()
    return opt

def update_option(option_id: int, *, text=None, is_correct=None):
    o = AnswerOption.query.get(option_id)
    if not o: return None
    changed = False
    if text is not None:
        t = (text or "").strip()
        if not t: raise ValueError("Texte de réponse requis.")
        if o.text != t: o.text = t; changed = True
    if is_correct is not None and bool(is_correct) != o.is_correct:
        o.is_correct = bool(is_correct); changed = True
    if changed: db.session.commit()
    return o

def delete_option(option_id: int) -> bool:
    o = AnswerOption.query.get(option_id)
    if not o: return False
    db.session.delete(o); db.session.commit()
    return True
