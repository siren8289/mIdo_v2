"""LLM 프롬프트 및 메시지 템플릿"""

LEVEL_NAMES = {
    "critical": "즉시 조치",
    "high": "빠른 조치",
    "medium": "계획 후 조치",
    "low": "관찰",
    "none": "문제 없음",
}


def make_prompt(report: dict) -> str:
    """Gemini에 전달할 취약점 분석 요약 프롬프트 생성"""
    summary = report["summary"]
    lines = [
        "너는 소프트웨어 보안 점검 도우미다.",
        "아래는 프로젝트 의존성을 자동 분석한 결과다.",
        "개발자가 무엇부터 해야 하는지 4문장 이내의 쉬운 한국어로 설명하라.",
        "숫자와 CVE 번호는 그대로 인용하고, 없는 사실을 지어내지 마라.",
        "마지막 문장은 '다음 할 일' 1개로 끝내라.",
        "",
        f"검사한 라이브러리 {summary['dependency_count']}개, 취약점 {summary['vulnerability_count']}건, "
        f"실제 악용 확인(KEV) {summary['kev_count']}건, 조치 단계 {LEVEL_NAMES.get(summary['level'], summary['level'])}",
        "",
        "우선순위 상위 취약점:",
    ]
    for finding in report["findings"][:5]:
        lines.append(
            f"- {finding['package']} {finding['version']} / {finding['cve_id'] or finding['vuln_id']} / "
            f"심각도 {finding['severity']} / 악용 확률(EPSS) {finding['epss']} / "
            f"KEV {'예' if finding['in_kev'] else '아니오'} / "
            f"약점 {finding['cwe_name']} (OWASP {finding['owasp']} {finding['owasp_name']}) / "
            f"ML 악용 위험 {finding['ml_exploit_risk']} / 수정 버전 {finding.get('fixed_version') or '없음'}"
        )
    return "\n".join(lines)
