import { Link, Route, Routes } from "react-router-dom";
import OwaspPage from "./pages/OwaspPage";
import ResultPage from "./pages/ResultPage";
import ScanPage from "./pages/ScanPage";

// 화면 뼈대: 위쪽 메뉴 + 주소(URL)에 따라 바뀌는 본문
export default function App() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      <header className="bg-white border-b border-slate-200 h-16 flex items-center px-6">
        <div className="w-full max-w-4xl mx-auto flex items-center gap-6">
          <span className="font-bold text-xl text-indigo-700">MIDO</span>
          <Link to="/" className="text-sm hover:text-indigo-700">의존성 분석</Link>
          <Link to="/owasp" className="text-sm hover:text-indigo-700">OWASP Top 10</Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto p-6">
        <Routes>
          <Route path="/" element={<ScanPage />} />
          <Route path="/scans/:id" element={<ResultPage />} />
          <Route path="/owasp" element={<OwaspPage />} />
        </Routes>
      </main>
    </div>
  );
}
