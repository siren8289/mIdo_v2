import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getScan, type Finding, type Scan } from "../api/api";

const LEVEL: Record<string, { label: string; color: string }> = {
  critical: { label: "즉시 조치", color: "bg-red-100 text-red-800" },
  high: { label: "빠른 조치", color: "bg-orange-100 text-orange-800" },
  medium: { label: "계획 후 조치", color: "bg-amber-100 text-amber-800" },
  low: { label: "관찰", color: "bg-slate-100 text-slate-700" },
  none: { label: "문제 없음", color: "bg-emerald-100 text-emerald-800" },
};

const SEVERITY_COLOR: Record<string, string> = {
  CRITICAL: "bg-red-100 text-red-800",
  HIGH: "bg-orange-100 text-orange-800",
  MEDIUM: "bg-amber-100 text-amber-800",
  LOW: "bg-slate-100 text-slate-700",
};

// 기능 1: 분석 결과 화면
export default function ResultPage() {
  const { id } = useParams();
  const [result, setResult] = useState<Scan | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    getScan(id)
      .then(setResult)
      .catch((e) => setError(e instanceof Error ? e.message : "결과를 불러오지 못했습니다."));
  }, [id]);

  if (error) return <p className="text-red-600">{error}</p>;
  if (!result) return <p className="text-slate-500">불러오는 중...</p>;

  const level = LEVEL[result.level] ?? LEVEL.none;
  const findings: Finding[] = result.findingsJson?.findings ?? [];

  return (
    <div className="space-y-4">
      <section className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
        <p className="text-sm text-slate-500">{result.fileType} · 라이브러리 {result.dependencyCount}개</p>
        <p className="text-4xl font-bold my-2">취약점 {result.vulnerabilityCount}건</p>
        <span className={`inline-block px-3 py-1 rounded-full text-sm font-bold ${level.color}`}>
          {level.label}
        </span>
        {result.kevCount > 0 && (
          <p className="text-sm text-red-700 mt-3">CISA KEV(실제 악용 확인) {result.kevCount}건</p>
        )}
      </section>

      <section className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
        <h3 className="font-bold mb-2">
          AI 설명{" "}
          <span className="text-xs font-normal text-slate-400">
            ({result.explanationSource === "gemini" ? "Gemini" : "기본 문장"})
          </span>
        </h3>
        <p className="text-sm leading-relaxed whitespace-pre-line">{result.explanation}</p>
      </section>

      {findings.map((item) => (
        <article key={item.vuln_id} className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100">
          <div className="flex flex-wrap items-center gap-2">
            <span className={`px-2 py-0.5 rounded text-xs font-bold ${SEVERITY_COLOR[item.severity] ?? SEVERITY_COLOR.LOW}`}>
              {item.severity}
            </span>
            {item.in_kev && <span className="px-2 py-0.5 rounded text-xs font-bold bg-red-600 text-white">KEV</span>}
            <span className="font-semibold">{item.cve_id || item.vuln_id}</span>
          </div>
          <p className="mt-2 text-sm font-medium">{item.package}@{item.version}</p>
          <p className="mt-1 text-sm text-slate-600">{item.summary}</p>
          <p className="mt-2 text-xs text-slate-500">
            CVSS {item.cvss_score} · EPSS {(item.epss * 100).toFixed(2)}% ·
            ML 악용 위험 {(item.ml_exploit_risk * 100).toFixed(1)}% ·
            {item.owasp} {item.owasp_name}
            {item.dl_severity ? ` · DL 추정 ${item.dl_severity}` : ""}
          </p>
          {item.fixed_version && (
            <p className="mt-1 text-sm text-indigo-700">고친 버전: {item.fixed_version} 이상</p>
          )}
          {item.source_url && (
            <a href={item.source_url} target="_blank" rel="noreferrer" className="mt-2 inline-block text-xs text-indigo-700 underline">
              OSV에서 근거 보기
            </a>
          )}
        </article>
      ))}

      {findings.length === 0 && (
        <p className="text-sm text-slate-500">확인된 취약점이 없습니다. 안전하다는 뜻은 아닙니다.</p>
      )}

      <Link to="/" className="block text-center text-sm text-indigo-700">← 다시 분석하기</Link>
    </div>
  );
}
