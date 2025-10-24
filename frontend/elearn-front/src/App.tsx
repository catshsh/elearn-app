import { Routes, Route } from "react-router-dom";
import CourseList from "./pages/CourseList";
import CourseDetailPage from "./pages/CourseDetail";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<CourseList />} />
      <Route path="/courses/:id" element={<CourseDetailPage />} />
    </Routes>
  );
}
