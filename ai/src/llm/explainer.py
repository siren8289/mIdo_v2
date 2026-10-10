"""LLM(Gemini) 기반 취약점 조치 설명 생성 및 Fallback 기본 설명"""
from src.core.config import GEMINI_API_KEY, GEMINI_MODEL
from src.llm.prompts import make_prompt


def basic_explanation(report: dict) -> str:
    """LLM API 미설정 또는 호출 실패 시 반환하는 규칙 기반 기본 설명"""
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


def explain(report: dict) -> tuple[str, str]:
    """(설명 문장, 설명 출처)를 반환한다. 출처는 'gemini' 또는 'basic'."""
    if not GEMINI_API_KEY or report["summary"]["vulnerability_count"] == 0:
        return basic_explanation(report), "basic"

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=types.HttpOptions(timeout=20000),
        )
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=make_prompt(report),
        )
        if response.text:
            return response.text.strip(), "gemini"
    except Exception as error:
        print("Gemini 호출 실패, 기본 설명을 사용합니다:", type(error).__name__)

    return basic_explanation(report), "basic"
