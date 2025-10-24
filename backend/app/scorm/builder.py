from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from markupsafe import Markup, escape
from typing import Any

from app.domain.models import Course, Lesson

def _xml_escape(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def build_scorm_zip(course: Course) -> BytesIO:
    """
    Construit un package SCORM 1.2 minimal pour `course`.
    - 1 SCO: index.html
    - pages chapitre: lesson-<lesson_id>-chapter-<chapter_id>.html
    - pages quiz: quiz-<lesson_id>.html (si questions)
    - imsmanifest.xml
    """
    mem = BytesIO()
    with ZipFile(mem, "w", ZIP_DEFLATED) as z:
        # wrapper API SCORM
        z.writestr("scorm_api.js", _SCORM_API_JS)
        # sommaire
        z.writestr("index.html", _render_index(course))
        # chapitres
        for l in course.lessons:
            for ch in l.chapters:
                z.writestr(f"lesson-{l.id}-chapter-{ch.id}.html", _render_chapter_page(course, l, ch))
        # quiz par leçon (si présent)
        for l in course.lessons:
            if l.quiz and l.quiz.questions:
                z.writestr(f"quiz-{l.id}.html", _render_quiz_page(course, l))
        # manifest
        z.writestr("imsmanifest.xml", _render_manifest(course))
    mem.seek(0)
    return mem

def _render_index(course: Course) -> str:
    items = []
    for l in course.lessons:
        items.append(f"<li><b>Leçon {l.index} — {escape(l.title or '')}</b><ul>")
        for ch in l.chapters:
            href = f"lesson-{l.id}-chapter-{ch.id}.html"
            items.append(f'<li><a href="{href}">Chapitre {ch.index}: {escape(ch.title or "")}</a></li>')
        if l.quiz and l.quiz.questions:
            items.append(f'<li><a href="quiz-{l.id}.html">Quiz de la leçon</a></li>')
        items.append("</ul></li>")
    toc = "\n".join(items)
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8" />
<title>{escape(course.title)} — Sommaire</title>
<script src="scorm_api.js"></script>
<style>
body{{font-family:system-ui,Segoe UI,Arial,sans-serif;max-width:900px;margin:24px auto;padding:12px}}
a{{text-decoration:none}}
a:hover{{text-decoration:underline}}
.card{{border:1px solid #ddd;border-radius:10px;padding:12px;margin-bottom:12px}}
</style>
</head>
<body>
<h1>{escape(course.title)}</h1>
<p>Nombre de leçons: {course.lesson_count} {("• Certification" if course.has_certification else "")}</p>
<div class="card">
  <h2>Sommaire</h2>
  <ol>{toc}</ol>
</div>
<script>
try {{ ScormApi.init(); }} catch(e) {{ console.log(e); }}
</script>
</body>
</html>"""

def _render_chapter_page(course: Course, lesson: Lesson, ch: Any) -> str:
    html = ch.html_content or ""
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8" />
<title>{escape(course.title)} — Leçon {lesson.index} — Chapitre {ch.index}</title>
<script src="scorm_api.js"></script>
<style>
body{{font-family:system-ui,Segoe UI,Arial,sans-serif;max-width:900px;margin:24px auto;padding:12px}}
.nav{{display:flex;gap:8px;margin-bottom:12px}}
.btn{{padding:6px 10px;border:1px solid #ccc;border-radius:8px;background:#f7f7f7;cursor:pointer}}
.btn:hover{{background:#eee}}
.card{{border:1px solid #ddd;border-radius:10px;padding:12px;margin-bottom:12px}}
</style>
</head>
<body>
<div class="nav">
  <a class="btn" href="index.html">← Sommaire</a>
</div>
<h1>Leçon {lesson.index} — {escape(lesson.title or "")}</h1>
<h2>Chapitre {ch.index} — {escape(ch.title or "")}</h2>
<div class="card">
{Markup(html)}
</div>
<script>
try {{
  ScormApi.init();
  ScormApi.set("cmi.core.lesson_status", "incomplete");
  ScormApi.commit();
}} catch(e) {{ console.log(e); }}
</script>
</body>
</html>"""

def _render_quiz_page(course: Course, lesson: Lesson) -> str:
    # données quiz -> JSON
    payload = []
    for qq in lesson.quiz.questions:
        payload.append({
            "id": qq.id,
            "index": qq.index,
            "text": qq.text,
            "type": qq.type,
            "options": [{"id": op.id, "text": op.text, "is_correct": op.is_correct} for op in qq.options],
        })
    import json
    data = json.dumps(payload, ensure_ascii=False)
    pass_threshold = 0.7  # 70%

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8" />
<title>{escape(course.title)} — Quiz leçon {lesson.index}</title>
<script src="scorm_api.js"></script>
<style>
body{{font-family:system-ui,Segoe UI,Arial,sans-serif;max-width:900px;margin:24px auto;padding:12px}}
.card{{border:1px solid #ddd;border-radius:10px;padding:12px;margin-bottom:12px}}
.btn{{padding:6px 10px;border:1px solid #ccc;border-radius:8px;background:#f7f7f7;cursor:pointer}}
.btn:hover{{background:#eee}}
.option{{border:1px solid #ddd;border-radius:8px;padding:6px 10px;margin:4px 0}}
.good{{background:#eaffea;border-color:#3cb371}}
.bad{{background:#ffecec;border-color:#dc143c}}
</style>
</head>
<body>
<a class="btn" href="index.html">← Sommaire</a>
<h1>Quiz — Leçon {lesson.index} : {escape(lesson.title or "")}</h1>
<div id="app" class="card"></div>

<script>
var QUESTIONS = {data};
var PASS = {pass_threshold};

function $(sel) {{ return document.querySelector(sel); }}

function render(checked, answers) {{
  if (checked === undefined) checked = false;
  if (!answers) answers = {{}};
  var root = document.getElementById("app");
  var html = "<ol>";

  for (var i=0; i<QUESTIONS.length; i++) {{
    var q = QUESTIONS[i];
    html += '<li style="margin-bottom:12px">';
    html += '<div style="margin-bottom:6;font-weight:600">' + q.index + '. ' + q.text +
            (q.type === 'multiple' ? ' <span style="font-size:12px;color:#666">(plusieurs réponses)</span>' : '') +
            '</div>';
    html += '<ul style="list-style:none;padding:0;margin:0">';
    var chosen = new Set(answers[q.id] || []);
    var good = new Set(q.options.filter(function(o){{return o.is_correct;}}).map(function(o){{return o.id;}}));

    for (var j=0; j<q.options.length; j++) {{
      var o = q.options[j];
      var sel = chosen.has(o.id);
      var cls = 'option';
      if (checked) {{
        if (o.is_correct) cls = 'option good';
        else if (sel) cls = 'option bad';
      }}
      var box = (q.type === 'single')
        ? '<input type="radio" name="q_' + q.id + '" ' + (sel ? 'checked' : '') + ' data-q="' + q.id + '" data-o="' + o.id + '" />'
        : '<input type="checkbox" ' + (sel ? 'checked' : '') + ' data-q="' + q.id + '" data-o="' + o.id + '" />';

      html += '<li class="' + cls + '">' + box + ' ' + o.text + '</li>';
    }}
    html += '</ul></li>';
  }}

  html += '</ol>';
  html += '<div style="display:flex;gap:12px;align-items:center">';
  if (!checked) {{
    html += '<button id="grade" class="btn">Corriger</button>';
  }} else {{
    html += '<b>Score :</b> <span id="score"></span> <button id="retry" class="btn">Recommencer</button>';
  }}
  html += '</div>';

  root.innerHTML = html;

  // inputs
  root.querySelectorAll('input').forEach(function(inp){{
    var qid = Number(inp.getAttribute('data-q'));
    var oid = Number(inp.getAttribute('data-o'));
    inp.addEventListener('change', function(){{ 
      if (!answers[qid]) answers[qid] = [];
      if (inp.type === 'radio') {{
        answers[qid] = [oid];
      }} else {{
        var set = new Set(answers[qid]);
        if (inp.checked) set.add(oid); else set.delete(oid);
        answers[qid] = Array.from(set);
      }}
    }});
  }});

  var gradeBtn = $('#grade');
  if (gradeBtn) gradeBtn.addEventListener('click', function() {{ doGrade(answers); }});

  var retryBtn = $('#retry');
  if (retryBtn) retryBtn.addEventListener('click', function() {{ render(false, {{}}); }});
}}

function doGrade(answers) {{
  var ok = 0;
  for (var i=0; i<QUESTIONS.length; i++) {{
    var q = QUESTIONS[i];
    var chosen = new Set(answers[q.id] || []);
    var good = new Set(q.options.filter(function(o){{return o.is_correct;}}).map(function(o){{return o.id;}}));
    var same = (chosen.size === good.size);
    if (same) {{
      var all = true;
      chosen.forEach(function(id){{ if(!good.has(id)) all = false; }});
      if (all) ok++;
    }}
  }}
  var total = QUESTIONS.length || 1;
  var score = Math.round((ok/total)*100);
  render(true, answers);
  document.getElementById('score').textContent = ok + ' / ' + total + ' (' + score + '%)';

  try {{
    ScormApi.init();
    ScormApi.set('cmi.core.score.raw', String(score));
    ScormApi.set('cmi.core.score.max', '100');
    ScormApi.set('cmi.core.lesson_status', (ok/total) >= PASS ? 'passed' : 'failed');
    ScormApi.commit();
  }} catch(e) {{ console.log(e); }}
}}

render(false, {{}});
</script>
</body>
</html>"""

def _render_manifest(course: Course) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="MANIFEST_{course.id}" version="1.2"
  xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
  xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.imsproject.org/xsd/imscp_rootv1p1p2 ims_xml.xsd
                      http://www.adlnet.org/xsd/adlcp_rootv1p2 adlcp_rootv1p2.xsd">
  <organizations default="ORG1">
    <organization identifier="ORG1">
      <title>{_xml_escape(course.title)}</title>
      <item identifier="ITEM1" identifierref="RES1" isvisible="true">
        <title>{_xml_escape(course.title)} — Module</title>
      </item>
    </organization>
  </organizations>
  <resources>
    <resource identifier="RES1" type="webcontent" adlcp:scormtype="sco" href="index.html">
      <file href="index.html"/>
      <file href="scorm_api.js"/>
    </resource>
  </resources>
</manifest>"""

_SCORM_API_JS = r"""(function(global){
  var api = null; var inited = false;
  function findAPI(win){
    var max = 500;
    while((!win.API) && (win.parent) && (win.parent != win) && max--) win = win.parent;
    return win.API || null;
  }
  var ScormApi = {
    init: function(){
      if(inited) return true;
      api = findAPI(window) || (window.opener ? findAPI(window.opener) : null);
      if(api && typeof api.LMSInitialize === "function"){
        var r = api.LMSInitialize("");
        inited = (r === "true" || r === true);
      } else {
        api = {
          LMSInitialize: function(){return "true";},
          LMSFinish: function(){return "true";},
          LMSSetValue: function(){return "true";},
          LMSCommit: function(){return "true";}
        };
        inited = true;
      }
      return inited;
    },
    set: function(element, value){
      if(!inited) this.init();
      try{ return api.LMSSetValue(element, String(value)); }catch(e){ return "false"; }
    },
    commit: function(){
      if(!inited) this.init();
      try{ return api.LMSCommit(""); }catch(e){ return "false"; }
    },
    finish: function(){
      if(!inited) this.init();
      try{ return api.LMSFinish(""); }catch(e){ return "false"; }
    }
  };
  global.ScormApi = ScormApi;
})(window);
"""