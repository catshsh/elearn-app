import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import type { CourseDetail as CourseDetailT, QuizDTO } from "../api";
import {
  getCourseDetail, addChapter, deleteChapter, updateChapter, getChapter, updateLesson,
  createQuizForLesson, getQuizByLesson, addQuestion, updateQuestion, deleteQuestion,
  addOption, updateOption, deleteOption
} from "../api";
import QuizPlayer from "../components/QuizPlayer";

export default function CourseDetailPage() {
  const { id } = useParams();
  const [data, setData] = useState<CourseDetailT | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  // Chapitres (CRUD)
  const [adding, setAdding] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [editingChapterId, setEditingChapterId] = useState<number | null>(null);
  const [editChapterTitle, setEditChapterTitle] = useState("");
  const [editContent, setEditContent] = useState("");

  // Leçons (édition titre)
  const [editingLessonId, setEditingLessonId] = useState<number | null>(null);
  const [editLessonTitle, setEditLessonTitle] = useState("");

  // Quiz (édition + prévisualisation)
  const [openQuizLessonId, setOpenQuizLessonId] = useState<number | null>(null);
  const [previewLessonId, setPreviewLessonId] = useState<number | null>(null);
  const [quiz, setQuiz] = useState<Record<number, QuizDTO | null>>({});
  const [busy, setBusy] = useState(false);

  // Édition locale (questions/options) pour ne pas “manger” les espaces
  const [qTextMap, setQTextMap] = useState<Record<number, string>>({});
  const [optTextMap, setOptTextMap] = useState<Record<number, string>>({});

  async function load() {
    try {
      setLoading(true);
      setData(await getCourseDetail(Number(id)));
      setErr(null);
    } catch (e: any) {
      setErr(e.message || "Erreur");
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => { load(); }, [id]);

  const firstLessonId = useMemo(() => data?.lessons?.[0]?.id, [data]);

  // ---- Utils ----
  async function refreshQuiz(lesson_id: number) {
    const q = await getQuizByLesson(lesson_id);
    setQuiz(prev => ({ ...prev, [lesson_id]: q }));
    const qdto = q as any;
    if (qdto && !("quiz" in qdto)) {
      const newQ: Record<number,string> = {};
      const newO: Record<number,string> = {};
      qdto.questions.forEach((qq: any) => {
        newQ[qq.id] = qq.text;
        qq.options.forEach((op: any) => { newO[op.id] = op.text; });
      });
      setQTextMap(newQ);
      setOptTextMap(newO);
    }
  }

  // ---- Chapitres ----
  async function onAddChapter(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget as HTMLFormElement;
    const f = new FormData(form);
    const lesson_id = Number(f.get("lesson_id"));
    const title = String(f.get("title") || "").trim();
    const html_content = String(f.get("html_content") || "");
    if (!lesson_id || !title) { alert("Leçon + titre requis"); return; }
    setAdding(true);
    try { await addChapter({ lesson_id, title, html_content }); form.reset(); await load(); }
    finally { setAdding(false); }
  }

  async function onDeleteChapter(cid: number) {
    if (!confirm("Supprimer ce chapitre ?")) return;
    setDeletingId(cid);
    try { await deleteChapter(cid); await load(); }
    finally { setDeletingId(null); }
  }

  async function startEditChapter(cid: number) {
    try {
      const ch = await getChapter(cid);
      setEditingChapterId(ch.id);
      setEditChapterTitle(ch.title);
      setEditContent(ch.html_content || "");
    } catch (e:any) {
      alert("Impossible de charger le chapitre : " + (e.message || "inconnue"));
    }
  }

  async function saveEditChapter(cid: number) {
    if (!editChapterTitle.trim()) { alert("Titre requis"); return; }
    await updateChapter(cid, { title: editChapterTitle.trim(), html_content: editContent });
    setEditingChapterId(null);
    await load();
  }

  // ---- Leçons ----
  function startEditLesson(lesson: {id:number; title:string}) {
    setEditingLessonId(lesson.id);
    setEditLessonTitle(lesson.title || "");
  }

  async function saveEditLesson(lid: number) {
    if (!editLessonTitle.trim()) { alert("Titre de leçon requis"); return; }
    await updateLesson(lid, { title: editLessonTitle.trim() });
    setEditingLessonId(null);
    await load();
  }

  // ---- Quiz (édition) ----
  async function toggleQuiz(lesson_id: number) {
    if (openQuizLessonId === lesson_id) { setOpenQuizLessonId(null); return; }
    setOpenQuizLessonId(lesson_id);
    if (!quiz[lesson_id]) {
      setBusy(true);
      try {
        await createQuizForLesson(lesson_id, "Quiz");
        await refreshQuiz(lesson_id);
      } catch (e:any) {
        alert("Quiz: " + (e.message || "erreur"));
      } finally {
        setBusy(false);
      }
    }
  }

  async function onAddQuestion(lesson_id: number) {
    const qdto = quiz[lesson_id] as any;
    if (!qdto || "quiz" in qdto || !qdto?.id) return;
    const res = await addQuestion(qdto.id, "Nouvelle question");
    setQTextMap(prev => ({ ...prev, [res.id]: "Nouvelle question" }));
    await refreshQuiz(lesson_id);
  }

  async function saveQuestion(lesson_id: number, question_id: number) {
    const text = (qTextMap[question_id] ?? "").toString();
    if (!text.trim()) { alert("Le texte de la question est requis"); return; }
    await updateQuestion(question_id, { text });
    await refreshQuiz(lesson_id);
  }

  async function onDeleteQuestion(lesson_id: number, question_id: number) {
    if (!confirm("Supprimer cette question ?")) return;
    await deleteQuestion(question_id);
    await refreshQuiz(lesson_id);
  }

  async function onAddOption(lesson_id: number, question_id: number) {
    const res = await addOption(question_id, "Réponse", false);
    setOptTextMap(prev => ({ ...prev, [res.id]: "Réponse" }));
    await refreshQuiz(lesson_id);
  }

  async function saveOption(lesson_id: number, option_id: number) {
    const text = (optTextMap[option_id] ?? "").toString();
    if (!text.trim()) { alert("Texte de réponse requis"); return; }
    await updateOption(option_id, { text });
    await refreshQuiz(lesson_id);
  }

  async function toggleCorrect(lesson_id: number, option_id: number, next: boolean) {
    await updateOption(option_id, { is_correct: next });
    await refreshQuiz(lesson_id);
  }

  async function onDeleteOption(lesson_id: number, option_id: number) {
    await deleteOption(option_id);
    await refreshQuiz(lesson_id);
  }

  // ---- Quiz (prévisualisation) ----
  async function openPreview(lesson_id: number) {
    setPreviewLessonId(lesson_id);
    if (!quiz[lesson_id]) {
      await createQuizForLesson(lesson_id, "Quiz");
      await refreshQuiz(lesson_id);
    }
  }
  function closePreview() {
    setPreviewLessonId(null);
  }

  if (loading) return <div style={{ padding: 16 }}>Chargement…</div>;
  if (err || !data) return <div style={{ padding: 16, color: "crimson" }}>{err || "Introuvable"}</div>;

  return (
    <div style={{ maxWidth: 900, margin: "24px auto", padding: 16, fontFamily: "sans-serif" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>{data.title}</h1>
        <Link to="/">← Retour</Link>
      </div>
      <p>{data.lesson_count} leçons {data.has_certification ? "• Certif ✅" : ""}</p>

      <h2 style={{ marginTop: 24 }}>Leçons</h2>
      <ol>
        {data.lessons.map(l => {
          const qdto = quiz[l.id] as any;
          const qLoaded = qdto && !("quiz" in qdto);

          return (
            <li key={l.id} style={{ marginBottom: 16 }}>
              {/* Titre leçon + actions */}
              {editingLessonId === l.id ? (
                <div style={{display:"flex", gap:8, alignItems:"center"}}>
                  <input value={editLessonTitle} onChange={e=>setEditLessonTitle(e.target.value)} />
                  <button onClick={()=>saveEditLesson(l.id)}>Enregistrer</button>
                  <button onClick={()=>setEditingLessonId(null)}>Annuler</button>
                </div>
              ) : (
                <div style={{display:"flex", gap:8, alignItems:"center"}}>
                  <b>Leçon {l.index}</b> — {l.title || "(sans titre)"}
                  <button onClick={()=>startEditLesson(l)}>Éditer</button>
                  <button onClick={()=>toggleQuiz(l.id)}>{openQuizLessonId===l.id ? "Fermer Quiz" : "Configurer le Quiz"}</button>
                  <button onClick={()=>openPreview(l.id)}>Prévisualiser</button>
                </div>
              )}

              {/* Prévisualisation du quiz */}
              {previewLessonId === l.id && qLoaded && (
                <QuizPlayer
                  questions={qdto.questions}
                  onClose={closePreview}
                />
              )}

              {/* Éditeur de quiz */}
              {openQuizLessonId === l.id && (
                <div style={{border:"1px dashed #aaa", padding:12, borderRadius:8, marginTop:8}}>
                  {busy ? <p>Chargement du quiz…</p> : (
                    (() => {
                      if (!qdto) return <p>Chargement…</p>;
                      if ("quiz" in qdto && qdto.quiz === null) return <p>Aucun quiz (il sera créé au besoin).</p>;
                      const q = qdto as Exclude<QuizDTO, {quiz:null}>;
                      return (
                        <div>
                          <div style={{display:"flex", justifyContent:"space-between", alignItems:"center"}}>
                            <h3 style={{margin:0}}>{q.title}</h3>
                            <button onClick={()=>onAddQuestion(l.id)}>+ Question</button>
                          </div>
                          <ol style={{marginTop:8}}>
                            {q.questions.map(qq => (
                              <li key={qq.id} style={{marginBottom:8}}>
                                <div style={{display:"flex", gap:8, alignItems:"center"}}>
                                  <input
                                    value={qTextMap[qq.id] ?? qq.text}
                                    onChange={(e)=>setQTextMap(prev=>({ ...prev, [qq.id]: e.target.value }))}
                                    style={{flex:1}}
                                  />
                                  <button onClick={()=>saveQuestion(l.id, qq.id)}>Enregistrer</button>
                                  <button onClick={()=>onDeleteQuestion(l.id, qq.id)}>Supprimer</button>
                                </div>
                                <ul style={{marginTop:6}}>
                                  {qq.options.map(op => (
                                    <li key={op.id} style={{display:"flex", gap:8, alignItems:"center", marginBottom:4}}>
                                      <input
                                        value={optTextMap[op.id] ?? op.text}
                                        onChange={(e)=>setOptTextMap(prev=>({ ...prev, [op.id]: e.target.value }))}
                                        style={{flex:1}}
                                      />
                                      <label style={{display:"flex", alignItems:"center", gap:4}}>
                                        <input
                                          type="checkbox"
                                          checked={op.is_correct}
                                          onChange={(e)=>toggleCorrect(l.id, op.id, e.target.checked)}
                                        />
                                        correcte
                                      </label>
                                      <button onClick={()=>saveOption(l.id, op.id)}>Enregistrer</button>
                                      <button onClick={()=>onDeleteOption(l.id, op.id)}>Supprimer</button>
                                    </li>
                                  ))}
                                  <li><button onClick={()=>onAddOption(l.id, qq.id)}>+ Réponse</button></li>
                                </ul>
                              </li>
                            ))}
                          </ol>
                        </div>
                      );
                    })()
                  )}
                </div>
              )}

              {/* Chapitres */}
              <ul style={{marginTop:8}}>
                {l.chapters.map(ch => (
                  <li key={ch.id} style={{marginBottom:8}}>
                    {editingChapterId === ch.id ? (
                      <div style={{display:"grid", gap:6}}>
                        <input value={editChapterTitle} onChange={e=>setEditChapterTitle(e.target.value)} />
                        <textarea rows={4} value={editContent} onChange={e=>setEditContent(e.target.value)} />
                        <div style={{display:"flex", gap:8}}>
                          <button onClick={()=>saveEditChapter(ch.id)}>Enregistrer</button>
                          <button onClick={()=>setEditingChapterId(null)}>Annuler</button>
                        </div>
                      </div>
                    ) : (
                      <div style={{display:"flex", alignItems:"center", gap:8}}>
                        <span>Chapitre {ch.index}: {ch.title}</span>
                        <button onClick={() => startEditChapter(ch.id)}>Éditer</button>
                        <button onClick={() => onDeleteChapter(ch.id)} disabled={deletingId === ch.id}>
                          {deletingId === ch.id ? "Suppression…" : "Supprimer"}
                        </button>
                      </div>
                    )}
                  </li>
                ))}
                {l.chapters.length === 0 && <li>(aucun chapitre)</li>}
              </ul>
            </li>
          );
        })}
      </ol>

      <h2 style={{ marginTop: 24 }}>Ajouter un chapitre</h2>
      <form onSubmit={onAddChapter} style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 8 }}>
        <input name="title" placeholder="Titre du chapitre" />
        <select name="lesson_id" defaultValue={firstLessonId ?? undefined}>
          {data.lessons.map(l => (
            <option key={l.id} value={l.id}>Leçon {l.index} — {l.title || "(sans titre)"} </option>
          ))}
        </select>
        <textarea name="html_content" placeholder="Contenu HTML…" rows={6} style={{ gridColumn: "1 / span 2" }} />
        <button type="submit" disabled={adding} style={{ gridColumn: "1 / span 2", justifySelf: "start" }}>
          {adding ? "Ajout…" : "Ajouter"}
        </button>
      </form>
    </div>
  );
}
