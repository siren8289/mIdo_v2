"""메인 기능 2개를 실제로 수행하는 곳.

기능 1. 의존성 위험 분석
  사용자가 붙여 넣은 package.json / requirements.txt / build.gradle / pom.xml 에서
  라이브러리를 뽑고, OSV·EPSS·KEV·CWE를 모은 뒤 ML·DL·LLM으로 우선순위를 매긴다.

기능 2. OWASP Top 10 현황
  data 파이프라인이 만든 공공데이터 통계를 그대로 보여 준다.
"""
import json
from collections import Counter
from pathlib import Path

from src.dependency_parser import parse_dependencies
from src.dl_model import predict_severity
from src.evidence import cwe_info, fetch_epss, is_in_kev, query_osv_all
from src.features import SEVERITY_TO_SCORE, make_ml_frame, severity_from_score
from src.llm_explain import explain
from src.ml_model import predict_exploit

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

# 심각도 글자를 숫자로 바꿔서 정렬할 때 쓴다. 숫자가 클수록 더 위험.
SEVERITY_RANK = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "UNKNOWN": 0}


def analyze(manifest_text):
    """기능 1: 의존성 파일을 받아 취약점 보고서를 만든다."""
    file_type, dependencies = parse_dependencies(manifest_text)
    if not dependencies:
        return _empty_report(file_type, "라이브러리 이름과 정확한 버전을 찾지 못했습니다.")

    # 1) OSV에서 라이브러리별 알려진 취약점을 찾는다.
    osv_results = query_osv_all(dependencies)
    findings = []
    for result in osv_results:
        findings.extend(result["vulns"])

    # 2) CVE가 있는 항목만 EPSS(악용 확률)를 한 번에 받아 온다.
    cve_ids = [item["cve_id"] for item in findings if item.get("cve_id")]
    epss_map = fetch_epss(cve_ids)

    # 3) CVSS 점수가 없는 취약점은 DL이 설명 글을 보고 심각도를 추정한다.
    need_dl = [item for item in findings if item.get("cvss_score") is None]
    dl_results = predict_severity([item["summary"] or item["details"] for item in need_dl])
    dl_by_id = {item["vuln_id"]: dl for item, dl in zip(need_dl, dl_results)}

    # 4) 각 취약점에 KEV / CWE / OWASP / ML 점수를 붙인다.
    enriched = [_enrich(item, epss_map, dl_by_id) for item in findings]
    if enriched:
        ml_scores = predict_exploit(make_ml_frame(enriched))
        for item, score in zip(enriched, ml_scores):
            item["ml_exploit_risk"] = score
            item["priority"] = _priority(item)
        enriched.sort(key=lambda item: item["priority"], reverse=True)

    report = {
        "file_type": file_type,
        "dependencies": dependencies,
        "findings": enriched,
        "summary": _summary(dependencies, enriched, osv_results),
        "owasp_breakdown": _owasp_breakdown(enriched),
    }
    # OSV를 못 불렀는데 취약점도 없으면, '없다'가 아니라 '조회 실패'로 설명한다.
    if report["summary"]["osv_failures"] and not enriched:
        report["explanation"] = (
            "OSV 취약점 조회에 실패했습니다. 인터넷 연결을 확인하고 다시 시도해 주세요."
        )
        report["explanation_source"] = "basic"
        return report
    explanation, source = explain(report)
    report["explanation"] = explanation
    report["explanation_source"] = source
    return report


def owasp_report():
    """기능 2: 공공데이터로 만든 OWASP Top 10 통계를 돌려준다."""
    path = MODELS_DIR / "owasp_stats.json"
    if not path.exists():
        return {"items": [], "total_cves": 0}
    items = json.loads(path.read_text(encoding="utf-8"))
    return {"items": items, "total_cves": sum(item.get("cve_count", 0) for item in items)}


def _enrich(item, epss_map, dl_by_id):
    """취약점 1건에 공공데이터·AI 결과를 붙인다."""
    info = cwe_info(item.get("cwe_id") or 0)
    cve_id = item.get("cve_id")
    score = item.get("cvss_score")
    dl = dl_by_id.get(item["vuln_id"])

    if score is not None:
        severity = severity_from_score(score)
        severity_source = "cvss"
    elif dl:
        severity = dl["label"]
        score = SEVERITY_TO_SCORE[severity]
        severity_source = "dl"
    else:
        severity = item.get("ghsa_severity") or "UNKNOWN"
        score = SEVERITY_TO_SCORE.get(severity, 0.0)
        severity_source = "osv"

    return {
        **item,
        "cvss_score": round(float(score), 1) if score else 0.0,
        "severity": severity,
        "severity_source": severity_source,
        "dl_severity": dl["label"] if dl else None,
        "dl_probability": dl["probability"] if dl else None,
        "epss": round(epss_map.get(cve_id, 0.0), 5) if cve_id else 0.0,
        "in_kev": bool(cve_id and is_in_kev(cve_id)),
        "cwe_name": info["name"],
        "owasp": info["owasp"],
        "owasp_name": info["owasp_name"],
        "ml_exploit_risk": 0.0,
        "priority": 0.0,
    }


def _priority(item):
    """숫자가 클수록 먼저 고쳐야 한다. KEV > EPSS > 심각도 > ML 순으로 더한다."""
    return (
        (100 if item["in_kev"] else 0)
        + item["epss"] * 40
        + SEVERITY_RANK.get(item["severity"], 0) * 8
        + item["ml_exploit_risk"] * 20
    )


def _summary(dependencies, findings, osv_results):
    kev_count = sum(1 for item in findings if item["in_kev"])
    vulnerable = {item["package"] for item in findings}
    failed = sum(1 for result in osv_results if result["error"])
    level = _level(findings, kev_count)
    return {
        "dependency_count": len(dependencies),
        "vulnerable_dependency_count": len(vulnerable),
        "vulnerability_count": len(findings),
        "kev_count": kev_count,
        "osv_failures": failed,
        "level": level,
    }


def _level(findings, kev_count):
    """화면에 보여 줄 한 줄 조치 단계"""
    if kev_count > 0 or any(item["severity"] == "CRITICAL" for item in findings):
        return "critical"
    if any(item["severity"] == "HIGH" or item["epss"] >= 0.1 or item["ml_exploit_risk"] >= 0.5 for item in findings):
        return "high"
    if findings:
        return "medium"
    return "none"


def _owasp_breakdown(findings):
    counts = Counter(item["owasp"] for item in findings)
    return [{"owasp": code, "count": count} for code, count in counts.most_common()]


def _empty_report(file_type, message):
    return {
        "file_type": file_type,
        "dependencies": [],
        "findings": [],
        "summary": {
            "dependency_count": 0,
            "vulnerable_dependency_count": 0,
            "vulnerability_count": 0,
            "kev_count": 0,
            "osv_failures": 0,
            "level": "none",
        },
        "owasp_breakdown": [],
        "explanation": message,
        "explanation_source": "basic",
    }
