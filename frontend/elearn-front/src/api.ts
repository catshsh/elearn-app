export const API = "http://127.0.0.1:5001";

export type Course = {
  id: number; title: string; lesson_count: number; has_certification: boolean;
  created_at: string; updated_at: string;
};

export type CourseDetail = Course & {
  lessons: { id: number; index: number; title: string; chapters: { id: number; index: number; title: string }[] }[];
};

export type QuizDTO = {
  id: number; lesson_id: number; title: string;
  questions: { id: number; index: number; text: string; type: "single"|"multiple";
    options: { id: number; text: string; is_correct: boolean }[];
  }[];
} | { quiz: null };

export async function listCourses(){ const r=await fetch(`${API}/api/courses`); if(!r.ok) throw new Error("Failed"); return r.json(); }
export async function createCourse(input:{title:string;lesson_count:number;has_certification:boolean}){ const r=await fetch(`${API}/api/courses`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(input)}); if(!r.ok) throw new Error("Failed"); return r.json(); }
export async function updateCourse(id:number, patch:Partial<{title:string;has_certification:boolean}>){ const r=await fetch(`${API}/api/courses/${id}`,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify(patch)}); if(!r.ok) throw new Error("Failed"); return r.json(); }
export async function deleteCourse(id:number){ const r=await fetch(`${API}/api/courses/${id}`,{method:"DELETE"}); if(!r.ok && r.status!==204) throw new Error("Failed"); }

export async function getCourseDetail(id:number){ const r=await fetch(`${API}/api/courses/${id}`); if(!r.ok) throw new Error("Not found"); return r.json(); }

export async function addChapter(input:{lesson_id:number;title:string;html_content:string}){ const r=await fetch(`${API}/api/chapters/add`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(input)}); if(!r.ok) throw new Error("Failed"); return r.json(); }
export async function getChapter(id:number){ const r=await fetch(`${API}/api/chapters/${id}`); if(!r.ok) throw new Error("Not found"); return r.json() as Promise<{id:number;lesson_id:number;index:number;title:string;html_content:string}>; }
export async function updateChapter(id:number, patch:Partial<{title:string;html_content:string}>){ const r=await fetch(`${API}/api/chapters/${id}`,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify(patch)}); if(!r.ok) throw new Error("Failed"); return r.json(); }
export async function deleteChapter(id:number){ const r=await fetch(`${API}/api/chapters/${id}`,{method:"DELETE"}); if(!r.ok && r.status!==204) throw new Error("Failed"); }
export async function updateLesson(id:number, patch:Partial<{title:string}>){ const r=await fetch(`${API}/api/lessons/${id}`,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify(patch)}); if(!r.ok) throw new Error("Failed to update lesson"); return r.json(); }

export async function createQuizForLesson(lesson_id:number, title="Quiz"){ const r=await fetch(`${API}/api/quizzes/create-for-lesson`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({lesson_id, title})}); if(!r.ok) throw new Error("Failed"); return r.json() as Promise<{id:number; lesson_id:number; title:string}>; }
export async function getQuizByLesson(lesson_id:number){ const r=await fetch(`${API}/api/quizzes/by-lesson/${lesson_id}`); if(!r.ok) throw new Error("Failed"); return r.json() as Promise<QuizDTO>; }

export async function addQuestion(quiz_id:number, text:string, type:"single"|"multiple"="single"){ const r=await fetch(`${API}/api/questions/add`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({quiz_id, text, type})}); if(!r.ok) throw new Error("Failed"); return r.json() as Promise<{id:number}>; }
export async function updateQuestion(id:number, patch:Partial<{text:string; type:"single"|"multiple"}>){ const r=await fetch(`${API}/api/questions/${id}`,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify(patch)}); if(!r.ok) throw new Error("Failed"); return r.json(); }
export async function deleteQuestion(id:number){ const r=await fetch(`${API}/api/questions/${id}`,{method:"DELETE"}); if(!r.ok && r.status!==204) throw new Error("Failed"); }

export async function addOption(question_id:number, text:string, is_correct=false){ const r=await fetch(`${API}/api/options/add`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({question_id, text, is_correct})}); if(!r.ok) throw new Error("Failed"); return r.json() as Promise<{id:number}>; }
export async function updateOption(id:number, patch:Partial<{text:string; is_correct:boolean}>){ const r=await fetch(`${API}/api/options/${id}`,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify(patch)}); if(!r.ok) throw new Error("Failed"); return r.json(); }
export async function deleteOption(id:number){ const r=await fetch(`${API}/api/options/${id}`,{method:"DELETE"}); if(!r.ok && r.status!==204) throw new Error("Failed"); }
