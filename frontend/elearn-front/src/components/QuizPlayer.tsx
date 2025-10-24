import { useMemo, useState } from "react";

type Option = { id:number; text:string; is_correct:boolean };
type Question = { id:number; index:number; text:string; type:"single"|"multiple"; options: Option[] };

export default function QuizPlayer({ questions, onClose }:{
  questions: Question[];
  onClose: () => void;
}) {
  // Réponses de l'étudiant
  const [answers, setAnswers] = useState<Record<number, number[]>>({}); // question_id -> option_ids cochés
  const [checked, setChecked] = useState(false);

  const total = questions.length;

  const score = useMemo(() => {
    if (!checked) return 0;
    let ok = 0;
    for (const q of questions) {
      const chosen = new Set(answers[q.id] || []);
      const good = new Set(q.options.filter(o=>o.is_correct).map(o=>o.id));

      // Exact match: toutes les bonnes et seulement les bonnes
      const sameSize = chosen.size === good.size;
      const sameElems = sameSize && [...chosen].every(id => good.has(id));
      if (sameElems) ok++;
    }
    return ok;
  }, [checked, answers, questions]);

  function toggleSingle(qid:number, oid:number) {
    setAnswers(prev => ({ ...prev, [qid]: [oid] }));
  }
  function toggleMulti(qid:number, oid:number, v:boolean) {
    setAnswers(prev => {
      const arr = new Set(prev[qid] || []);
      if (v) arr.add(oid); else arr.delete(oid);
      return { ...prev, [qid]: [...arr] };
    });
  }

  return (
    <div style={{border:"2px solid #444", borderRadius:12, padding:16, marginTop:12, background:"#fafafa"}}>
      <div style={{display:"flex", justifyContent:"space-between", alignItems:"center"}}>
        <h3 style={{margin:0}}>Prévisualisation du quiz</h3>
        <button onClick={onClose}>Fermer</button>
      </div>

      <ol style={{marginTop:12}}>
        {questions.map(q => (
          <li key={q.id} style={{marginBottom:12}}>
            <div style={{marginBottom:6, fontWeight:600}}>
              {q.index}. {q.text} {q.type === "multiple" ? <span style={{fontSize:12, color:"#666"}}>(plusieurs réponses)</span> : null}
            </div>

            <ul style={{listStyle:"none", padding:0, margin:0, display:"grid", gap:6}}>
              {q.options.map(o => {
                const selected = new Set(answers[q.id] || []);
                const isSelected = selected.has(o.id);
                const showSolution = checked;
                const isGood = o.is_correct;

                // feedback visuel (après correction)
                const style: React.CSSProperties = showSolution
                  ? (isGood ? {border:"1px solid #3cb371", background:"#eaffea"} :
                               (isSelected ? {border:"1px solid #dc143c", background:"#ffecec"} : {border:"1px solid #ddd"}))
                  : {border:"1px solid #ddd"};

                return (
                  <li key={o.id} style={{...style, borderRadius:8, padding:"6px 10px", display:"flex", alignItems:"center", gap:8}}>
                    {q.type === "single" ? (
                      <input
                        type="radio"
                        name={`q_${q.id}`}
                        checked={isSelected}
                        onChange={() => toggleSingle(q.id, o.id)}
                      />
                    ) : (
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={e => toggleMulti(q.id, o.id, e.target.checked)}
                      />
                    )}
                    <span>{o.text}</span>
                    {showSolution && isGood && <span style={{marginLeft:"auto", fontSize:12, color:"#3cb371"}}>correct</span>}
                    {showSolution && !isGood && isSelected && <span style={{marginLeft:"auto", fontSize:12, color:"#dc143c"}}>incorrect</span>}
                  </li>
                );
              })}
            </ul>
          </li>
        ))}
      </ol>

      <div style={{display:"flex", alignItems:"center", gap:12, marginTop:12}}>
        {!checked ? (
          <button onClick={()=>setChecked(true)}>Corriger</button>
        ) : (
          <>
            <b>Score :</b> {score} / {total}
            <button onClick={() => { setChecked(false); setAnswers({}); }}>Recommencer</button>
          </>
        )}
      </div>
    </div>
  );
}
