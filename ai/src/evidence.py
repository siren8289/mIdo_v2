"""취약점 근거(evidence) 모으기

- OSV  (실시간 API) : 라이브러리 이름 + 버전 → 알려진 취약점 목록
- EPSS (실시간 API) : CVE 번호 → 30일 안에 악용될 확률
- KEV  (파일)       : data 파이프라인이 만든 '실제 악용된 CVE' 목록
- CWE  (파일)       : CWE 번호 → 이름, OWASP 분류
"""
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx

from src.features import cvss3_base_score

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
OSV_URL = "https://api.osv.dev/v1/query"
EPSS_URL = "https://api.first.org/data/v1/epss"
TIMEOUT_SECONDS = 10

# OSV 가 쓰는 생태계 이름
OSV_ECOSYSTEMS = {"npm": "npm", "pypi": "PyPI", "maven": "Maven"}

# GitHub 보안 권고(GHSA)의 등급 이름을 CVSS 등급 이름으로 맞춘다.
GHSA_SEVERITY = {"CRITICAL": "CRITICAL", "HIGH": "HIGH", "MODERATE": "MEDIUM", "MEDIUM": "MEDIUM", "LOW": "LOW"}


# ---------- 파일에서 읽는 근거 (KEV, CWE) ----------

_kev = None
_cwe = None


def load_lookups():
    """처음 한 번만 파일을 읽는다."""
    global _kev, _cwe
    if _kev is None:
        _kev = set(json.loads((MODELS_DIR / "kev_cves.json").read_text(encoding="utf-8")))
        _cwe = json.loads((MODELS_DIR / "cwe_info.json").read_text(encoding="utf-8"))
    return _kev, _cwe


def is_in_kev(cve_id):
    kev, _ = load_lookups()
    return cve_id in kev


def cwe_info(cwe_id):
    """CWE 번호 → {"name": ..., "owasp": "A05", "owasp_name": "인젝션"}"""
    _, cwe = load_lookups()
    return cwe.get(str(cwe_id), {"name": "Unknown", "owasp": "OTHER", "owasp_name": "Top 10 외"})


# ---------- OSV ----------

def query_osv(dependency):
    """라이브러리 1개의 취약점 목록. 실패하면 error 메시지를 같이 돌려준다."""
    payload = {
        "package": {"name": dependency["name"], "ecosystem": OSV_ECOSYSTEMS[dependency["ecosystem"]]},
        "version": dependency["version"],
    }
    try:
        response = httpx.post(OSV_URL, json=payload, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        vulns = response.json().get("vulns") or []
        return {"dependency": dependency, "vulns": [parse_osv_vuln(v, dependency) for v in vulns], "error": None}
    except httpx.HTTPError as error:
        return {"dependency": dependency, "vulns": [], "error": type(error).__name__}


def query_osv_all(dependencies):
    """여러 라이브러리를 동시에(최대 8개씩) 조회해서 기다리는 시간을 줄인다."""
    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(query_osv, dependencies))


def parse_osv_vuln(vuln, dependency):
    """OSV 응답 1건 → 우리 서비스가 쓰는 모양"""
    aliases = vuln.get("aliases") or []
    cve_ids = [alias for alias in aliases if alias.startswith("CVE-")]
    if vuln.get("id", "").startswith("CVE-"):
        cve_ids.insert(0, vuln["id"])

    # CVSS v3 벡터 찾기 (v4 는 계산식이 달라서 쓰지 않는다)
    vector = None
    for item in vuln.get("severity") or []:
        if item.get("type") == "CVSS_V3":
            vector = item.get("score")
    score = cvss3_base_score(vector) if vector else None

    database = vuln.get("database_specific") or {}
    cwe_ids = database.get("cwe_ids") or []
    cwe_number = int(cwe_ids[0].split("-")[1]) if cwe_ids and cwe_ids[0].startswith("CWE-") else 0

    return {
        "vuln_id": vuln.get("id"),
        "cve_id": cve_ids[0] if cve_ids else None,
        "package": dependency["name"],
        "version": dependency["version"],
        "ecosystem": dependency["ecosystem"],
        "summary": vuln.get("summary") or (vuln.get("details") or "")[:300],
        "details": (vuln.get("details") or "")[:1000],
        "cvss_vector": vector,
        "cvss_score": score,
        "ghsa_severity": GHSA_SEVERITY.get(str(database.get("severity", "")).upper()),
        "cwe_id": cwe_number,
        "fixed_version": find_fixed_version(vuln, dependency["name"]),
        "source_url": f"https://osv.dev/vulnerability/{vuln.get('id')}",
    }


def find_fixed_version(vuln, package_name):
    """'몇 버전부터 고쳐졌는지' 찾는다. 없으면 None."""
    for affected in vuln.get("affected") or []:
        if affected.get("package", {}).get("name") != package_name:
            continue
        for range_info in affected.get("ranges") or []:
            for event in range_info.get("events") or []:
                if "fixed" in event:
                    return event["fixed"]
    return None


# ---------- EPSS ----------

def fetch_epss(cve_ids):
    """CVE 여러 개의 EPSS 점수를 한 번에 가져온다. 실패하면 빈 dict."""
    if not cve_ids:
        return {}
    try:
        response = httpx.get(EPSS_URL, params={"cve": ",".join(sorted(cve_ids)[:100])}, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        return {row["cve"]: float(row["epss"]) for row in response.json().get("data", [])}
    except (httpx.HTTPError, ValueError, KeyError):
        return {}
