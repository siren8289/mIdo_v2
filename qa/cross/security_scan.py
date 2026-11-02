#!/usr/bin/env python3
"""제품 파일을 읽어 정적 보안 검사를 한다. qa/ 와 node_modules 는 보지 않는다."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _read(rel: str) -> tuple[str, list[str]]:
    file = ROOT / rel
    text = file.read_text(encoding="utf-8")
    return text, text.splitlines()


def _line(lines: list[str], needle: str) -> str:
    for index, line in enumerate(lines, start=1):
        if needle in line:
            return str(index)
    return "UNKNOWN"


def _function(lines: list[str], line_no: str) -> str:
    if line_no == "UNKNOWN":
        return "UNKNOWN"
    index = int(line_no) - 1
    for cursor in range(index, -1, -1):
        stripped = lines[cursor].strip()
        if stripped.startswith("def "):
            return stripped.split("(")[0].replace("def ", "")
        if "function " in stripped:
            return stripped.split("function ", 1)[1].split("(")[0].strip()
        if stripped.startswith("public ") or stripped.startswith("private "):
            parts = stripped.split("(")[0].split()
            return parts[-1] if parts else "UNKNOWN"
    return "UNKNOWN"


def _item(tc_id, status, rel, lines, needle, expected, actual, evidence, cause="", input_value=""):
    line = _line(lines, needle) if needle else "UNKNOWN"
    return {
        "id": tc_id,
        "status": status,
        "expected": expected,
        "actual": actual,
        "evidence": evidence,
        "file": rel,
        "function": _function(lines, line),
        "line": line,
        "input": input_value,
        "error": "" if status != "FAIL" else actual,
        "cause": cause,
    }


def main() -> None:
    cases = []
    result_text, result_lines = _read("front/src/pages/ResultPage.tsx")
    href = "href={item.source_url}" in result_text
    allow = "startsWith(\"https" in result_text or "protocol" in result_text
    href_bad = href and not allow
    cases.append(_item(
        "SEC-HREF", "FAIL" if href_bad else "PASS",
        "front/src/pages/ResultPage.tsx", result_lines, "href={item.source_url}",
        "source_url은 https 등 허용 스킴만 링크",
        "href에 source_url을 넣고 스킴 검사가 없음" if href_bad else "스킴 검사 있음 또는 href 없음",
        "ResultPage 원문 검색",
        "javascript: URL이 앵커 href로 들어갈 수 있다." if href_bad else "",
        "source_url=javascript:alert(1)",
    ))

    fallback = "LEVEL[result.level] ?? LEVEL.none" in result_text
    safe_label = 'label: "문제 없음"' in result_text
    level_bad = fallback and safe_label
    cases.append(_item(
        "SEC-LEVEL", "FAIL" if level_bad else "PASS",
        "front/src/pages/ResultPage.tsx", result_lines, "LEVEL[result.level] ?? LEVEL.none",
        "알 수 없는 level은 '문제 없음'이 아님",
        "없는 키는 LEVEL.none(문제 없음)으로 떨어짐" if level_bad else "안전 기본값 아님",
        "폴백 식과 none 라벨 확인",
        "알 수 없는 위험 등급을 안전으로 보여 준다." if level_bad else "",
        "level=unknown",
    ))

    key_bad = "key={item.vuln_id}" in result_text
    cases.append(_item(
        "SEC-REACT-KEY", "FAIL" if key_bad else "PASS",
        "front/src/pages/ResultPage.tsx", result_lines, "key={item.vuln_id}",
        "같은 vuln_id가 겹쳐도 키가 충돌하지 않음",
        "key가 vuln_id뿐이라 중복 시 React 키가 충돌" if key_bad else "중복 안전 키",
        "key= 원문",
        "vuln_id 중복 시 카드 키가 같다." if key_bad else "",
    ))

    app_text, app_lines = _read("front/src/App.tsx")
    missing_404 = 'path="*"' not in app_text and "path='*'" not in app_text
    cases.append(_item(
        "SEC-NO-404", "FAIL" if missing_404 else "PASS",
        "front/src/App.tsx", app_lines, "<Routes>",
        "없는 경로용 path=* 라우트",
        "path=* 없음" if missing_404 else "catch-all 있음",
        "App.tsx Routes 검색",
        "매칭되지 않는 URL에 404 화면이 없다." if missing_404 else "",
        "/no-such-page",
    ))

    danger_text = ""
    danger_hit = False
    danger_file = "front/src"
    danger_lines: list[str] = []
    for file in (ROOT / "front" / "src").rglob("*"):
        if file.suffix.lower() not in {".tsx", ".ts", ".jsx", ".js"}:
            continue
        body = file.read_text(encoding="utf-8")
        if "dangerouslySetInnerHTML" in body:
            danger_hit = True
            danger_file = str(file.relative_to(ROOT))
            danger_text = body
            danger_lines = body.splitlines()
            break
    if not danger_hit:
        danger_lines = ["dangerouslySetInnerHTML"]
    cases.append(_item(
        "SEC-NO-DANGEROUS", "FAIL" if danger_hit else "PASS",
        danger_file if danger_hit else "front/src",
        danger_lines if danger_hit else ["// none"],
        "dangerouslySetInnerHTML" if danger_hit else "",
        "dangerouslySetInnerHTML 없음",
        "사용" if danger_hit else "front/src에서 0건",
        "front/src 원문 검색",
        "HTML 삽입 API가 있다." if danger_hit else "",
    ))

    nginx, nginx_lines = _read("front/nginx.conf")
    tls_bad = "listen 80" in nginx and "listen 443" not in nginx
    cases.append(_item(
        "SEC-TLS", "FAIL" if tls_bad else "PASS",
        "front/nginx.conf", nginx_lines, "listen 80",
        "공개 프런트에 TLS 리스너",
        "listen 80만 있고 443이 없음" if tls_bad else "443 또는 80 아님",
        "nginx.conf 원문",
        "배포 nginx가 평문 HTTP만 연다." if tls_bad else "",
    ))

    deploy, deploy_lines = _read(".github/workflows/deploy.yml")
    checkout_bad = "actions/checkout@v4" in deploy and "workflow_run.head_sha" not in deploy
    cases.append(_item(
        "SEC-CHECKOUT", "FAIL" if checkout_bad else "PASS",
        ".github/workflows/deploy.yml", deploy_lines, "actions/checkout@v4",
        "workflow_run이 검사한 head_sha를 checkout",
        "checkout@v4에 head_sha ref 없음" if checkout_bad else "head_sha ref 있음",
        "deploy.yml 원문",
        "CI가 검사한 커밋과 다른 기본 브랜치를 체크아웃할 수 있다." if checkout_bad else "",
    ))

    handler, handler_lines = _read("back/src/main/java/com/mido/global/exception/GlobalExceptionHandler.java")
    generic = 'return error(HttpStatus.INTERNAL_SERVER_ERROR, "INTERNAL_ERROR", "서버 오류가 발생했습니다.");' in handler
    cases.append(_item(
        "SEC-GENERIC-500", "PASS" if generic else "FAIL",
        "back/src/main/java/com/mido/global/exception/GlobalExceptionHandler.java",
        handler_lines, "서버 오류가 발생했습니다.",
        "미처리 예외 본문은 고정 문장",
        "고정 문장 반환" if generic else "고정 문장 없음",
        "handleUnexpected 반환 문장",
        "" if generic else "예외 문자열이 응답에 섞일 수 있다.",
    ))

    sql_hit = None
    sql_rel = "back/src/main/java"
    sql_lines = ["// none"]
    for file in (ROOT / "back" / "src" / "main").rglob("*.java"):
        body = file.read_text(encoding="utf-8")
        if "nativeQuery" in body or "createNativeQuery" in body or "createQuery(" in body:
            sql_hit = file
            sql_rel = str(file.relative_to(ROOT))
            sql_lines = body.splitlines()
            break
    cases.append(_item(
        "SEC-NO-SQL", "FAIL" if sql_hit else "PASS",
        sql_rel, sql_lines, "nativeQuery" if sql_hit else "",
        "문자열로 잇는 SQL 또는 native query 없음",
        f"발견: {sql_rel}" if sql_hit else "back/src/main java 0건",
        "java 원문 검색",
        "native query 문자열이 있다." if sql_hit else "",
    ))

    scan, scan_lines = _read("back/src/main/java/com/mido/scan/service/ScanService.java")
    empty_bad = "scanRepository.save" in scan and "has(\"summary\")" not in scan and "isEmpty(" not in scan
    cases.append(_item(
        "SEC-EMPTY-AI", "FAIL" if empty_bad else "PASS",
        "back/src/main/java/com/mido/scan/service/ScanService.java",
        scan_lines, "scanRepository.save",
        "summary가 없는 AI JSON은 저장하지 않음",
        "save 전에 summary/empty 검사가 없음" if empty_bad else "빈 응답 검사 있음",
        "ScanService.analyze 원문",
        "빈 ObjectNode도 저장된다." if empty_bad else "",
        "{}",
    ))

    epss, epss_lines = _read("ai/src/evidence/epss.py")
    clamp = "max(0" in epss or "0 <=" in epss or "min(1" in epss
    raw = 'float(row["epss"])' in epss
    epss_bad = raw and not clamp
    cases.append(_item(
        "SEC-EPSS", "FAIL" if epss_bad else "PASS",
        "ai/src/evidence/epss.py", epss_lines, 'float(row["epss"])',
        "EPSS는 0 이상 1 이하로 제한",
        "float 변환만 하고 clamp가 없음" if epss_bad else "clamp 있음",
        "fetch_epss 반환식. 라이브 HTTP는 호출하지 않음",
        "범위 밖 값이 그대로 점수에 들어간다." if epss_bad else "",
        "epss=-0.1 또는 1.5",
    ))

    print(json.dumps({"tool": "security_scan", "cases": cases}, ensure_ascii=False))


if __name__ == "__main__":
    main()
