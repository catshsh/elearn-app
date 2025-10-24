import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import type { Course } from "../api";
import { listCourses, createCourse, deleteCourse, updateCourse } from "../api";

export default function CourseList() {
  const [items, setItems] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editCertif, setEditCertif] = useState(false);

  async function load() {
    try {
      setLoading(true);
      setItems(await listCourses());
      setErr(null);
    } catch (e: any) {
      setErr(e.message || "Erreur");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function onCreate(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const title = String(f.get("title") || "").trim();
    const lesson_count = Number(f.get("lesson_count") || 1);
    const has_certification = Boolean(f.get("has_certification"));
    if (!title) { alert("Titre requis"); return; }
    setCreating(true);
    try {
      await createCourse({ title, lesson_count, has_certification });
      (e.currentTarget as HTMLFormElement).reset();
      await load();
    } finally {
      setCreating(false);
    }
  }

  async function onDeleteCourse(id: number) {
    if (!confirm("Supprimer ce module et toutes ses leçons/chapitres ?")) return;
    setDeletingId(id);
    try {
      await deleteCourse(id);
      await load();
    } finally {
      setDeletingId(null);
    }
  }

  function startEdit(c: Course) {
    setEditingId(c.id);
    setEditTitle(c.title);
    setEditCertif(c.has_certification);
  }

  async function saveEdit(id: number) {
    if (!editTitle.trim()) { alert("Titre requis"); return; }
    await updateCourse(id, { title: editTitle.trim(), has_certification: editCertif });
    setEditingId(null);
    await load();
  }

  return (
    <div style={{maxWidth: 900, margin: "24px auto", padding: 16, fontFamily:"sans-serif"}}>
      <h1>eLearning — Cours</h1>

      <form onSubmit={onCreate} style={{display:"grid", gridTemplateColumns:"2fr 1fr auto auto", gap: 8, margin:"12px 0 20px"}}>
        <input name="title" placeholder="Titre…" />
        <input name="lesson_count" type="number" min={1} defaultValue={3} />
        <label style={{display:"flex", alignItems:"center", gap:6}}>
          <input type="checkbox" name="has_certification" />Certif
        </label>
        <button disabled={creating}>{creating ? "Création…" : "Créer"}</button>
      </form>

      {loading ? <p>Chargement…</p> : err ? <p style={{color:"crimson"}}>{err}</p> : (
        items.length === 0 ? <p>(aucun cours pour l’instant)</p> : (
          <ul style={{listStyle:"none", padding:0, display:"grid", gap:8}}>
            {items.map(c => (
              <li key={c.id} style={{border:"1px solid #ddd", borderRadius:8, padding:12}}>
                {editingId === c.id ? (
                  <div style={{display:"grid", gridTemplateColumns:"1fr auto auto", gap:8, alignItems:"center"}}>
                    <div>
                      <input value={editTitle} onChange={e=>setEditTitle(e.target.value)} />
                      <label style={{marginLeft:12}}>
                        <input type="checkbox" checked={editCertif} onChange={e=>setEditCertif(e.target.checked)} />
                        {" "}Certif
                      </label>
                    </div>
                    <button onClick={()=>saveEdit(c.id)}>Enregistrer</button>
                    <button onClick={()=>setEditingId(null)}>Annuler</button>
                  </div>
                ) : (
                  <div style={{display:"flex", justifyContent:"space-between", alignItems:"center", gap:12}}>
                    <div style={{flex:1}}>
                      <b>{c.title}</b> — {c.lesson_count} leçons {c.has_certification ? "• Certif ✅" : ""}
                      <div style={{fontSize:12, color:"#666"}}>Créé le {new Date(c.created_at).toLocaleString()}</div>
                    </div>
                    <div style={{display:"flex", gap:8}}>
                      <button onClick={()=>startEdit(c)}>Éditer</button>
                      <Link to={`/courses/${c.id}`}>Détail →</Link>
                      <a
                        href={`http://127.0.0.1:5001/api/export/scorm/${c.id}`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Exporter SCORM
                      </a>
                      <button onClick={() => onDeleteCourse(c.id)} disabled={deletingId === c.id}>
                        {deletingId === c.id ? "Suppression…" : "Supprimer"}
                      </button>
                    </div>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )
      )}
    </div>
  );
}
