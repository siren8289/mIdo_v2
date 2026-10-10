"""기능 1: 의존성 취약점 분석 및 우선순위 평가 오케스트레이션

매니페스트 파싱 → OSV/EPSS/KEV 취약점 수집 → DL 심각도 추론 → ML 악용 위험 예측 → LLM 조치 가이드 생성
"""
from collections import Counter

from src.core.config import SEVERITY_RANK
from src.evidence import cwe_info, fetch_epss, is_in_kev, query_osv_all
from src.inference import predict_exploit, predict_severity
from src.llm import explain
from src.parser import parse_dependencies
from src.scoring import SEVERITY_TO_SCORE, make_ml_frame, severity_from_score


def analyze(manifest_text: str) -> dict:
    """의존성 파일을 받아 전체 보안 분석 및 우선순위 정렬 리포트를 생성한다."""
    file_type, dependencies = parse_dependencies(manifest_text)
    if not dependencies:
        return _empty_report(file_type, "라이브러리 이름과 정확한 버전을 찾지 못했습니다.")

    # 1) OSV에서 라이브러리별 알려진 취약점을 동시 조회
    osv_results = query_osv_all(dependencies)
    findings = []
    for result in osv_results:
        findings.extend(result["vulns"])

    # 2) CVE 식별자가 있는 항목 대상 EPSS(악용 확률) 일괄 조회
    cve_ids = [item["cve_id"] for item in findings if item.get("cve_id")]
    epss_map = fetch_epss(cve_ids)

    # 3) CVSS 점수가 누락된 취약점은 DL 모델로 설명 텍스트 기반 심각도 추정
    need_dl = [item for item in findings if item.get("cvss_score") is None]
    dl_results = predict_severity([item["summary"] or item["details"] for item in need_dl])
    dl_by_id = {item["vuln_id"]: dl for item, dl in zip(need_dl, dl_results)}

    # 4) 각 취약점에 KEV / CWE / OWASP / ML 악용 위험 점수 부착
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

    # OSV 조회 실패로 인해 취약점이 없는 경우 에러 안내
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


def _enrich(item: dict, epss_map: dict[str, float], dl_by_id: dict[str, dict]) -> dict:
    """취약점 1건에 외부 위협 인텔리전스 및 모델 추론 결과를 결합한다."""
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


def _priority(item: dict) -> float:
    """조치 우선순위 산출: KEV(100) > EPSS(40) > 심각도(32) > ML 악용위험(20) 가중합"""
    return (
        (100 if item["in_kev"] else 0)
        + item["epss"] * 40
        + SEVERITY_RANK.get(item["severity"], 0) * 8
        + item["ml_exploit_risk"] * 20
    )


def _summary(dependencies: list[dict], findings: list[dict], osv_results: list[dict]) -> dict:
    """분석 결과 전체 수치 요약"""
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


def _level(findings: list[dict], kev_count: int) -> str:
    """최종 조치 권고 레벨 결정 (critical / high / medium / none)"""
    if kev_count > 0 or any(item["severity"] == "CRITICAL" for item in findings):
        return "critical"
    if any(item["severity"] == "HIGH" or item["epss"] >= 0.1 or item["ml_exploit_risk"] >= 0.5 for item in findings):
        return "high"
    if findings:
        return "medium"
    return "none"


def _owasp_breakdown(findings: list[dict]) -> list[dict]:
    """OWASP Top 10 항목별 취약점 발생 빈도 집계"""
    counts = Counter(item["owasp"] for item in findings)
    return [{"owasp": code, "count": count} for code, count in counts.most_common()]


def _empty_report(file_type: str, message: str) -> dict:
    """의존성 파싱 실패 또는 분석 대상이 없을 때 반환하는 빈 리포트"""
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
