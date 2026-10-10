"""OSV (Open Source Vulnerabilities) API 실시간 조회 및 취약점 정보 파싱"""
from concurrent.futures import ThreadPoolExecutor

import httpx

from src.core.config import (
    GHSA_SEVERITY,
    OSV_ECOSYSTEMS,
    OSV_URL,
    TIMEOUT_SECONDS,
)
from src.scoring.cvss import cvss3_base_score


def query_osv(dependency: dict):
    """라이브러리 1개의 취약점 목록을 조회한다. 실패 시 error 메시지를 함께 반환."""
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


def query_osv_all(dependencies: list[dict]):
    """여러 라이브러리를 멀티스레드(최대 8개)로 동시 조회하여 대기 시간을 단축한다."""
    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(query_osv, dependencies))


def parse_osv_vuln(vuln: dict, dependency: dict):
    """OSV 원본 응답 1건을 서비스 표준 포맷으로 변환한다."""
    aliases = vuln.get("aliases") or []
    cve_ids = [alias for alias in aliases if alias.startswith("CVE-")]
    if vuln.get("id", "").startswith("CVE-"):
        cve_ids.insert(0, vuln["id"])

    # CVSS v3 벡터 추출 (v4는 가중치 산식이 달라 지원하지 않음)
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


def find_fixed_version(vuln: dict, package_name: str):
    """취약점이 해결된 최소 버전(fixed version)을 찾는다. 없으면 None 반환."""
    for affected in vuln.get("affected") or []:
        if affected.get("package", {}).get("name") != package_name:
            continue
        for range_info in affected.get("ranges") or []:
            for event in range_info.get("events") or []:
                if "fixed" in event:
                    return event["fixed"]
    return None
