import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createScan } from "../api/api";

// 화면에 미리 넣어 두는 예시. 버튼을 누르면 입력칸에 채워진다.
const SAMPLES: Record<string, string> = {
  "package.json": `{
  "dependencies": {
    "lodash": "4.17.15",
    "minimist": "1.2.0"
  }
}`,
  "requirements.txt": "requests==2.19.0\nflask==1.0.2\n",
  "build.gradle": "dependencies {\n    implementation 'org.apache.logging.log4j:log4j-core:2.14.1'\n}\n",
};

// 기능 1: 의존성 파일을 붙여 넣고 분석한다.
export default function ScanPage() {
  const navigate = useNavigate();
  const [manifest, setManifest] = useState(SAMPLES["package.json"]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    if (manifest.trim().length < 3) {
      setError("의존성 파일 내용을 붙여 넣어 주세요.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const result = await createScan(manifest);
      navigate(`/scans/${result.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "분석에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 space-y-4">
      <h2 className="text-xl font-bold">의존성 위험 분석</h2>
      <p className="text-sm text-slate-500">
        package.json, requirements.txt, build.gradle, pom.xml 내용을 붙여 넣으면
        OSV·EPSS·KEV를 조회하고 ML·DL·LLM으로 우선순위를 매깁니다.
      </p>

      <div className="flex flex-wrap gap-2">
        {Object.keys(SAMPLES).map((name) => (
          <button
            key={name}
            type="button"
            onClick={() => setManifest(SAMPLES[name])}
            className="px-3 py-1 text-xs rounded-full border border-slate-200 hover:border-indigo-400"
          >
            {name} 예시
          </button>
        ))}
      </div>

      <textarea
        className="w-full h-64 font-mono text-sm border border-slate-200 rounded-xl p-3"
        value={manifest}
        onChange={(e) => setManifest(e.target.value)}
        placeholder='{"dependencies":{"lodash":"4.17.15"}}'
      />

      {error && <p className="text-sm text-red-600">{error}</p>}

      <button
        onClick={handleSubmit}
        disabled={loading}
        className="w-full py-3 rounded-xl bg-indigo-700 text-white font-bold disabled:opacity-50"
      >
        {loading ? "AI가 분석하는 중..." : "분석하기"}
      </button>
    </div>
  );
}
