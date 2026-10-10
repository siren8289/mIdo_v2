import { useEffect, useState } from "react";
import { getOwaspReport, type OwaspReport } from "../api/api";

// 기능 2: 공공데이터로 만든 OWASP Top 10 현황
export default function OwaspPage() {
  const [report, setReport] = useState<OwaspReport | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getOwaspReport()
      .then(setReport)
      .catch((e) => setError(e instanceof Error ? e.message : "통계를 불러오지 못했습니다."));
  }, []);

  if (error) return <p className="text-red-600">{error}</p>;
  if (!report) return <p className="text-slate-500">불러오는 중...</p>;

  return (
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 space-y-4">
      <h2 className="text-xl font-bold">OWASP Top 10:2025 현황</h2>
      <p className="text-sm text-slate-500">
        NVD + EPSS + CISA KEV + CWE를 전처리한 결과입니다. 최근 공개 CVE {report.total_cves.toLocaleString()}건.
      </p>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500 border-b">
              <th className="py-2">분류</th>
              <th>이름</th>
              <th className="text-right">CVE 수</th>
              <th className="text-right">평균 CVSS</th>
              <th className="text-right">평균 EPSS</th>
              <th className="text-right">KEV 비율</th>
            </tr>
          </thead>
          <tbody>
            {report.items.map((item) => (
              <tr key={item.owasp} className="border-b border-slate-100">
                <td className="py-2 font-mono">{item.owasp}</td>
                <td>{item.owasp_name}</td>
                <td className="text-right">{item.cve_count.toLocaleString()}</td>
                <td className="text-right">{item.avg_cvss.toFixed(2)}</td>
                <td className="text-right">{(item.avg_epss * 100).toFixed(2)}%</td>
                <td className="text-right">{(item.kev_rate * 100).toFixed(2)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
