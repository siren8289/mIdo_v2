"""LLM(Gemini)으로 분석 결과를 '개발자가 바로 할 일' 중심으로 설명한다.

GEMINI_API_KEY 가 없거나 호출에 실패하면 미리 정한 기본 문장을 쓴다.
"""
import os

LEVEL_NAMES = {
    "critical": "즉시 조치",
    "high": "빠른 조치",
    "medium": "계획 후 조치",
    "low": "관찰",
    "none": "문제 없음",
}


def basic_explanation(report):
    """LLM 없이 만드는 기본 설명"""
    summary = report["summary"]
    if summary["vulnerability_count"] == 0:
        return (
            "OSV에서 알려진 취약점이 발견되지 않았습니다. "
            "아직 공개되지 않은 취약점이 있을 수 있으니 의존성을 주기적으로 점검하세요."
        )

    top = report["findings"][0]
    text = (
        f"라이브러리 {summary['dependency_count']}개 중 {summary['vulnerable_dependency_count']}개에서 "
        f"취약점 {summary['vulnerability_count']}건이 발견되었습니다. "
    )
    if summary["kev_count"] > 0:
        text += (
            f"그중 {summary['kev_count']}건은 실제 공격에 쓰인 것이 확인된 취약점(CISA KEV)이라 "
            "가장 먼저 처리해야 합니다. "
        )
    text += f"가장 급한 것은 {top['package']} {top['version']}의 {top['cve_id'] or top['vuln_id']}입니다."
    if top.get("fixed_version"):
        text += f" {top['fixed_version']} 버전 이상으로 올리면 해결됩니다."
    return text


def make_prompt(report):
    """Gemini에 넣을 질문 글"""
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


def explain(report):
    """(설명 문장, 출처)를 돌려준다. 출처는 gemini 또는 basic."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or report["summary"]["vulnerability_count"] == 0:
        return basic_explanation(report), "basic"

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=20000),
        )
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=make_prompt(report),
        )
        if response.text:
            return response.text.strip(), "gemini"
    except Exception as error:
        print("Gemini 호출 실패, 기본 설명을 사용합니다:", type(error).__name__)

    return basic_explanation(report), "basic"
