// Spring 서버와 통신하는 함수를 한 곳에 모았다.

const API_URL: string = import.meta.env.VITE_API_URL ?? "http://localhost:8080";

export type Finding = {
  vuln_id: string;
  cve_id: string | null;
  package: string;
  version: string;
  ecosystem: string;
  summary: string;
  severity: string;
  severity_source: string;
  cvss_score: number;
  epss: number;
  in_kev: boolean;
  cwe_id: number;
  cwe_name: string;
  owasp: string;
  owasp_name: string;
  ml_exploit_risk: number;
  dl_severity: string | null;
  fixed_version: string | null;
  source_url: string;
};

export type Scan = {
  id: number;
  fileType: string;
  dependencyCount: number;
  vulnerabilityCount: number;
  kevCount: number;
  level: string;
  explanation: string;
  explanationSource: string;
  findingsJson: {
    findings?: Finding[];
    owasp_breakdown?: { owasp: string; count: number }[];
    dependencies?: { name: string; version: string; ecosystem: string }[];
  };
};

export type OwaspItem = {
  owasp: string;
  owasp_name: string;
  cve_count: number;
  avg_cvss: number;
  avg_epss: number;
  kev_rate: number;
  exploit_rate: number;
};

export type OwaspReport = {
  items: OwaspItem[];
  total_cves: number;
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(API_URL + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    let message = "요청에 실패했습니다.";
    try {
      const body = await response.json();
      message = body.message ?? message;
    } catch {
      // JSON이 아니면 기본 문장을 쓴다.
    }
    throw new Error(message);
  }
  return response.json();
}

export function createScan(manifest: string) {
  return request<Scan>("/api/scans", { method: "POST", body: JSON.stringify({ manifest }) });
}

export function getScan(id: string) {
  return request<Scan>(`/api/scans/${id}`);
}

export function getOwaspReport() {
  return request<OwaspReport>("/api/owasp");
}
