#!/usr/bin/env python3
"""QA gate. From repo root: python3 qa/run.py

Follows qa-policy.md. Dual-tool results go to
qa/results/<area>/<section>/<YYYY-MM-DD>/ (five English-named day files).
Does not modify product code.
"""
import json
import os
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qa.recorder import CaseResult, RiskNote, RunRecord, now_seoul, run_id, write_run

def _section_map() -> dict[str, str]:
    path = ROOT / "qa" / "config" / "section-map.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("by_tc", {})
    except (OSError, json.JSONDecodeError):
        return {}

PYTEST_NAMES = {
    "test_package_json": "UNIT-PKG",
    "test_requirements": "UNIT-REQ",
    "test_cvss_log4shell": "UNIT-CVSS-10",
    "test_cwe_and_owasp": "UNIT-CWE",
    "test_severity": "UNIT-SEV",
    "test_clean_nvd_drops_rejected": "UNIT-NVD",
    "test_build_dataset_label": "UNIT-LABEL",
    "test_processed_files_exist": "UNIT-FILES",
}
GRADLE_NAMES = {
    "emptyManifestReturns400": "API-EMPTY",
    "createAndGet": "API-CREATE",
}

# source_a / source_b 는 아래 버킷 이름이다.
CASES = [
    ("UNIT-PKG", "unit", "package.json 파서", "agree", True, "", "", "", "", "NONE",
     "lodash ^4.17.15와 vite 5.0.0을 버전으로 읽는다.", "python3 qa/cross/direct_checks.py",
     "pytest", "direct_checks.py", "pytest", "direct"),
    ("UNIT-REQ", "unit", "requirements.txt 파서", "agree", True, "", "", "", "", "NONE",
     "requests==2.19.0만 남고 주석과 >= 는 빠진다.", "python3 qa/cross/direct_checks.py",
     "pytest", "direct_checks.py", "pytest", "direct"),
    ("UNIT-CVSS-10", "unit", "CVSS v3.1 Log4Shell", "agree", True, "", "", "", "", "NONE",
     "공식 벡터의 기본 점수는 10.0이다.", "python3 qa/cross/direct_checks.py",
     "pytest", "direct_checks.py", "pytest", "direct"),
    ("UNIT-CWE", "unit", "CWE·OWASP 매핑", "agree", True, "", "", "", "", "NONE",
     "CWE-79는 79와 A05, 미매핑은 OTHER다.", "python3 qa/cross/direct_checks.py",
     "pytest", "direct_checks.py", "pytest", "direct"),
    ("UNIT-SEV", "unit", "CVSS 심각도 구간", "agree", True, "", "", "", "", "NONE",
     "9.8/7.5/5.0/1.2는 CRITICAL/HIGH/MEDIUM/LOW다.", "python3 qa/cross/direct_checks.py",
     "pytest", "direct_checks.py", "pytest", "direct"),
    ("UNIT-NVD", "unit", "NVD Rejected 제거", "agree", True, "", "", "", "", "NONE",
     "Rejected CVE는 표에 남지 않는다.", "python3 qa/cross/direct_checks.py",
     "pytest", "direct_checks.py", "pytest", "direct"),
    ("UNIT-LABEL", "unit", "학습 라벨", "agree", True, "", "", "", "", "NONE",
     "KEV·높은 EPSS 행의 exploit_label은 1이다.", "python3 qa/cross/direct_checks.py",
     "pytest", "direct_checks.py", "pytest", "direct"),
    ("UNIT-FILES", "unit", "전처리 산출물", "agree", True, "", "", "", "", "NONE",
     "owasp/cwe/kev 정리 파일이 저장소에 있다.", "python3 qa/cross/direct_checks.py",
     "pytest", "direct_checks.py", "pytest", "direct"),
    ("API-EMPTY", "api", "빈 manifest 거절", "agree", True, "", "", "", "", "NONE",
     "빈 문자열 manifest는 Bean Validation과 MockMvc 모두 거절한다.",
     "cd back && ./gradlew test --tests com.mido.scan.ScanControllerTest.emptyManifestReturns400",
     "gradle test", "api_rules.py", "gradle", "rules"),
    ("API-NULL", "api", "null manifest", "one_sided", False, "", "", "", "", "NONE",
     "null 거절은 규칙 재구현만 실행했다.", "python3 qa/cross/api_rules.py",
     "gradle test", "api_rules.py", "none", "rules"),
    ("API-BLANK", "api", "공백 manifest", "one_sided", False, "", "", "", "", "NONE",
     "공백 거절은 규칙 재구현만 실행했다.", "python3 qa/cross/api_rules.py",
     "gradle test", "api_rules.py", "none", "rules"),
    ("API-SHORT", "api", "2자 manifest", "one_sided", False, "", "", "", "", "NONE",
     "길이 2 거절은 규칙 재구현만 실행했다.", "python3 qa/cross/api_rules.py",
     "gradle test", "api_rules.py", "none", "rules"),
    ("API-MIN", "api", "3자 manifest", "one_sided", False, "", "", "", "", "NONE",
     "길이 3 허용은 규칙 재구현만 실행했다.", "python3 qa/cross/api_rules.py",
     "gradle test", "api_rules.py", "none", "rules"),
    ("API-MAX", "api", "80000자 manifest", "one_sided", False, "", "", "", "", "NONE",
     "80000자 허용은 규칙 재구현만 실행했다.", "python3 qa/cross/api_rules.py",
     "gradle test", "api_rules.py", "none", "rules"),
    ("API-OVER", "api", "80001자 manifest", "one_sided", False, "", "", "", "", "NONE",
     "80001자 거절은 규칙 재구현만 실행했다.", "python3 qa/cross/api_rules.py",
     "gradle test", "api_rules.py", "none", "rules"),
    ("API-CREATE", "api", "스캔 저장 후 조회", "one_sided", False, "", "", "", "", "NONE",
     "createAndGet는 MockMvc만 실행했다.", "cd back && ./gradlew test",
     "gradle test", "api_rules.py", "gradle", "none"),
    ("SEC-HREF", "security", "결과 링크 스킴", "agree", True, "HIGH",
     "저장된 source_url을 결과 화면이 그대로 연다.",
     "javascript: URL이면 클릭한 사용자의 브라우저에서 스크립트가 실행된다.",
     "허용 스킴(https)만 href에 넣는다.", "MD-03-023",
     "source_url에 스킴 허용 목록이 있는지 두 도구가 파일을 읽는다.",
     "node qa/cross/ui_checks.mjs",
     "security_scan.py", "ui_checks.mjs", "security", "node"),
    ("SEC-LEVEL", "security", "알 수 없는 위험 등급", "agree", True, "HIGH",
     "서버가 명세 밖 level을 주면 화면이 none으로 떨어진다.",
     "취약점이 있어도 '문제 없음'으로 보여 조치가 지연된다.",
     "unknown은 안전 라벨로 바꾸지 않는다.", "MD-03-010",
     "unknown level의 라벨이 '문제 없음'이 아닌지 확인한다.",
     "node qa/cross/ui_checks.mjs",
     "security_scan.py", "ui_checks.mjs", "security", "node"),
    ("SEC-REACT-KEY", "security", "결과 카드 키", "agree", True, "MEDIUM",
     "같은 vuln_id가 두 번 오면 키가 겹친다.",
     "React가 카드를 잘못 재사용해 다른 취약점 내용이 붙을 수 있다.",
     "인덱스 등 유일한 키를 쓴다.", "MD-03-026",
     "ResultPage의 key 속성을 두 도구가 읽는다.",
     "node qa/cross/ui_checks.mjs",
     "security_scan.py", "ui_checks.mjs", "security", "node"),
    ("SEC-NO-404", "security", "없는 경로", "agree", True, "LOW",
     "사용자가 없는 URL을 연다.",
     "빈 본문만 보여 경로 오류인지 알 수 없다.",
     "path=* 404 화면을 둔다.", "MD-01-008",
     "App.tsx에 catch-all 라우트가 있는지 확인한다.",
     "node qa/cross/ui_checks.mjs",
     "security_scan.py", "ui_checks.mjs", "security", "node"),
    ("SEC-NO-DANGEROUS", "security", "HTML 삽입 API", "agree", True, "", "", "", "", "NONE",
     "front/src에 dangerouslySetInnerHTML이 없다.",
     "node qa/cross/ui_checks.mjs",
     "security_scan.py", "ui_checks.mjs", "security", "node"),
    ("SEC-TLS", "security", "nginx TLS", "agree", True, "MEDIUM",
     "compose가 프런트 80번을 호스트에 연다.",
     "같은 망의 관찰자가 분석 요청과 결과를 평문으로 볼 수 있다.",
     "로컬 전용이 아니면 TLS를 종료한다.", "MD-30-013",
     "nginx.conf의 listen을 두 도구가 읽는다.",
     "node qa/cross/ui_checks.mjs",
     "security_scan.py", "ui_checks.mjs", "security", "node"),
    ("SEC-CHECKOUT", "security", "CD checkout ref", "agree", True, "MEDIUM",
     "workflow_run 완료 시 deploy가 checkout한다.",
     "CI가 검사한 SHA가 아닌 기본 브랜치 팁이 이미지로 빌드될 수 있다.",
     "actions/checkout ref에 workflow_run.head_sha를 넣는다.", "MD-30-039",
     "deploy.yml을 두 도구가 읽는다.",
     "node qa/cross/ui_checks.mjs",
     "security_scan.py", "ui_checks.mjs", "security", "node"),
    ("SEC-GENERIC-500", "security", "500 응답 본문", "agree", True, "", "", "", "", "NONE",
     "미처리 예외의 JSON 본문은 고정 문장이다.",
     "node qa/cross/ui_checks.mjs",
     "security_scan.py", "ui_checks.mjs", "security", "node"),
    ("SEC-NO-SQL", "security", "SQL 조합", "agree", True, "", "", "", "", "NONE",
     "백엔드 메인 소스에 native query 문자열이 없다.",
     "python3 qa/cross/rg_rules.py",
     "security_scan.py", "rg", "security", "rg"),
    ("SEC-EMPTY-AI", "security", "빈 AI JSON 저장", "agree", True, "MEDIUM",
     "AI가 {} 를 반환한다.",
     "내용 없는 분석이 201로 저장된다.",
     "summary가 없으면 저장하지 않고 오류를 반환한다.", "MD-05-017",
     "ScanService 저장 가드를 두 도구가 본다. 이번 실행은 HTTP를 열지 않는다.",
     "python3 qa/cross/rg_rules.py",
     "security_scan.py", "rg", "security", "rg"),
    ("SEC-EPSS", "security", "EPSS 범위", "agree", True, "MEDIUM",
     "EPSS 응답이 0 미만이거나 1 초과다.",
     "우선순위 점수가 왜곡된다. 라이브 API는 호출하지 않았다.",
     "0 이상 1 이하가 아니면 버리거나 잘라 낸다.", "MD-14-017",
     "EPSS 값은 0과 1 사이로 제한된다.",
     "python3 qa/cross/security_scan.py 와 python3 qa/cross/rg_rules.py",
     "security_scan.py", "rg", "security", "rg"),
    ("SEC-TOOL-UNKNOWN", "security", "미등록 에이전트 도구", "agree", True, "HIGH",
     "모델이 목록에 없는 도구 이름을 넘긴다.",
     "파일 수정만 막고 그 외 도구는 허용되어 가드레일이 우회된다.",
     "허용 목록에 있는 도구만 실행한다.", "MD-25-019",
     "등록되지 않은 도구는 거부된다.",
     "python3 qa/cross/direct_checks.py",
     "direct_checks.py", "rg", "direct", "rg"),
    ("SEC-TOOL-DENY", "security", "file_edit 거부", "agree", True, "", "", "", "", "NONE",
     "금지 목록의 file_edit은 거부된다.",
     "python3 qa/cross/direct_checks.py",
     "direct_checks.py", "rg", "direct", "rg"),
    ("SEC-CVSS-SX", "security", "잘못된 CVSS scope", "agree", True, "MEDIUM",
     "S:X 또는 빈 S.",
     "유효하지 않은 벡터가 높은 점수로 계산된다.",
     "S가 U/C가 아니면 None을 반환한다.", "MD-15-022",
     "잘못된 scope는 점수가 되면 안 된다.",
     "python3 qa/cross/direct_checks.py",
     "direct_checks.py", "rg", "direct", "rg"),
    ("SEC-CAP", "security", "의존성 50개 절단", "agree", True, "MEDIUM",
     "package.json 의존성 51개.",
     "51번째 이후 취약점을 검사하지 않고 사용자에게 알리지 않는다.",
     "잘렸음을 응답에 포함한다.", "MD-09-067",
     "51개 의존성은 조용히 50개로 줄지 않는다.",
     "python3 qa/cross/direct_checks.py",
     "direct_checks.py", "rg", "direct", "rg"),
    ("SEC-DUP", "security", "package.json 중복", "agree", True, "MEDIUM",
     "dependencies와 devDependencies에 같은 패키지.",
     "같은 라이브러리 취약점이 두 번 집계된다.",
     "parse_package_json에서 이름 기준으로 한 건만 남긴다.", "MD-09-026",
     "같은 패키지는 한 건만 남는다.",
     "python3 qa/cross/direct_checks.py",
     "direct_checks.py", "rg", "direct", "rg"),
    ("SEC-OWASP-NEG", "security", "OWASP 음수 합계", "agree", True, "MEDIUM",
     "cve_count가 -1인 항목.",
     "전체 CVE 수가 실제보다 작아지거나 음수가 된다.",
     "0 미만 건수는 합계에 넣지 않는다.", "MD-20-009",
     "음수 cve_count는 합계를 줄이지 않는다.",
     "python3 qa/cross/direct_checks.py",
     "direct_checks.py", "rg", "direct", "rg"),
    ("SEC-OWASP-CORRUPT", "security", "OWASP JSON 파손", "agree", True, "MEDIUM",
     "owasp_stats.json 내용이 { 이다.",
     "JSONDecodeError가 API까지 올라간다.",
     "파손 파일을 오류 dict로 바꾼다.", "MD-20-007",
     "깨진 OWASP JSON은 예외로 올라가지 않는다.",
     "python3 qa/cross/direct_checks.py",
     "direct_checks.py", "rg", "direct", "rg"),
    ("SEC-KEV-MISSING", "security", "KEV 파일 부재", "agree", True, "MEDIUM",
     "kev_cves.json이 없다.",
     "FileNotFoundError로 분석 준비 실패가 구분되지 않는다.",
     "파일 부재를 준비 상태 오류로 반환한다.", "MD-14-026",
     "KEV 파일이 없어도 FileNotFoundError가 아니다.",
     "python3 qa/cross/direct_checks.py",
     "direct_checks.py", "rg", "direct", "rg"),
    ("REG-FRONT", "regression", "프런트 타입체크와 빌드", "both_must_pass", True, "", "", "", "", "NONE",
     "tsc --noEmit과 vite build가 모두 성공한다.",
     "cd front && npx tsc --noEmit && npx vite build",
     "tsc --noEmit", "vite build", "tsc", "vite"),
    ("INFRA-COMPOSE", "infra", "compose healthcheck 정의", "agree", True, "MEDIUM",
     "compose.yaml에 서비스·healthcheck가 없다.",
     "배포 시 준비 완료 전 트래픽이 들어갈 수 있다.",
     "front/back/ai와 healthcheck를 정의한다.", "NONE",
     "compose.yaml에 front/back/ai·healthcheck가 있고 Dockerfile이 있다.",
     "python3 qa/cross/compose_checks.py && python3 qa/cross/dockerfile_checks.py",
     "compose_checks.py", "dockerfile_checks.py", "compose", "dockerfiles"),
    ("INFRA-SMOKE", "infra", "로컬 HTTP 스모크", "both_must_pass", True, "MEDIUM",
     "로컬 스택이 기동되지 않았거나 포트가 닫혀 있다.",
     "배포 스모크 없이 PASS하면 실제 요청 실패를 놓친다.",
     "스택 기동 후 front·back HTTP 스모크를 확인한다. 미기동은 NOT_RUN.", "NONE",
     "front(80)과 back(8080) HTTP 스모크가 모두 성공한다. 미기동이면 NOT_RUN.",
     "python3 qa/cross/http_smoke.py",
     "http_smoke front", "http_smoke back", "smoke_front", "smoke_back"),
]


def _run(args: list[str], cwd: Path, timeout: int, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        args, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout, check=False,
    )


def _json_tool(args: list[str], timeout: int) -> dict:
    try:
        proc = _run(args, ROOT, timeout)
    except subprocess.TimeoutExpired as exc:
        return {"_error": f"timeout {timeout}s {exc}", "cases": []}
    raw = proc.stdout.strip()
    try:
        data = json.loads(raw) if raw else {"cases": []}
    except json.JSONDecodeError:
        data = {"cases": []}
    if proc.returncode != 0 and not data.get("cases"):
        data["_error"] = (proc.stderr or raw or f"exit {proc.returncode}")[-800:]
    elif data.get("error"):
        data["_error"] = data["error"]
    return data


def _index(data: dict | None) -> dict[str, dict]:
    if not data:
        return {}
    return {item["id"]: item for item in data.get("cases", []) if "id" in item}


def _junit(path: Path) -> dict[str, tuple[str, str]]:
    found: dict[str, tuple[str, str]] = {}
    if not path.exists():
        return found
    root = ET.parse(path).getroot()
    for case in root.iter("testcase"):
        name = case.get("name") or ""
        failure = case.find("failure")
        error = case.find("error")
        if failure is not None:
            found[name] = ("FAIL", (failure.get("message") or failure.text or "failure")[:400])
        elif error is not None:
            found[name] = ("ERROR", (error.get("message") or error.text or "error")[:400])
        else:
            found[name] = ("PASS", "junit 통과")
    return found


def _norm_test_name(name: str) -> str:
    return name[:-2] if name.endswith("()") else name


def _status_from_map(names: dict[str, str], found: dict[str, tuple[str, str]], prefix: str) -> dict[str, dict]:
    normalized = {_norm_test_name(name): value for name, value in found.items()}
    out = {}
    for test_name, tc_id in names.items():
        if test_name not in normalized:
            out[tc_id] = {
                "id": tc_id, "status": "NOT_RUN", "expected": test_name,
                "actual": "junit에 없음", "evidence": prefix, "file": "UNKNOWN",
                "function": test_name, "line": "UNKNOWN", "error": "", "cause": "", "input": "",
            }
            continue
        status, message = normalized[test_name]
        out[tc_id] = {
            "id": tc_id, "status": status, "expected": "테스트 통과",
            "actual": message if status != "PASS" else "통과",
            "evidence": f"{prefix} {test_name}: {message}",
            "file": "UNKNOWN", "function": test_name, "line": "UNKNOWN",
            "error": message if status != "PASS" else "", "cause": message if status != "PASS" else "",
            "input": "",
        }
    return out


def _missing(tc_id: str, status: str, evidence: str) -> dict:
    return {
        "id": tc_id, "status": status, "expected": "", "actual": evidence,
        "evidence": evidence, "file": "UNKNOWN", "function": "UNKNOWN", "line": "UNKNOWN",
        "error": evidence if status == "ERROR" else "", "cause": evidence if status == "ERROR" else "",
        "input": "",
    }


def _decide(mode: str, left: str, right: str) -> str:
    if mode == "one_sided":
        return "NOT_RUN"
    if mode == "both_must_pass":
        if "ERROR" in (left, right):
            return "ERROR"
        if left == "PASS" and right == "PASS":
            return "PASS"
        if "NOT_RUN" in (left, right):
            return "NOT_RUN"
        return "FAIL"
    if left == "NOT_RUN" or right == "NOT_RUN":
        return "NOT_RUN"
    if left == "ERROR" or right == "ERROR":
        return "ERROR"
    if left == right:
        return left
    return "ERROR"


def _loc(primary: dict, secondary: dict) -> tuple[str, str, str]:
    for source in (primary, secondary):
        file = source.get("file") or "UNKNOWN"
        if file not in {"", "UNKNOWN"}:
            return file, source.get("function") or "UNKNOWN", str(source.get("line") or "UNKNOWN")
    return "UNKNOWN", "UNKNOWN", "UNKNOWN"


def _bucket(name: str, buckets: dict[str, dict[str, dict]], tc_id: str) -> dict:
    if name == "none":
        return _missing(tc_id, "NOT_RUN", "이 도구는 이 TC를 실행하지 않았다")
    data = buckets.get(name, {})
    if "_error" in data and tc_id not in data:
        return _missing(tc_id, "ERROR", data["_error"])
    return data.get(tc_id) or _missing(tc_id, "NOT_RUN", f"{name} 결과에 {tc_id}가 없다")


def main() -> int:
    moment = now_seoul()
    started = moment.isoformat(timespec="seconds")
    current = run_id(moment)
    sha = _run(["git", "rev-parse", "--short=12", "HEAD"], ROOT, 20)
    commit = sha.stdout.strip() or "UNKNOWN"
    dirty = _run(["git", "status", "--porcelain"], ROOT, 20)
    if dirty.stdout.strip():
        commit += "+dirty"

    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([str(ROOT / "ai"), str(ROOT), env.get("PYTHONPATH", "")])
    junit = Path("/tmp") / f"mido-qa-pytest-{current}.xml"
    pytest = _run(
        [sys.executable, "-m", "pytest", "-q", f"--junitxml={junit}",
         "ai/tests/test_parser.py", "data/tests/test_transform.py"],
        ROOT, 180, env,
    )
    pytest_found = _junit(junit)
    pytest_error = ""
    if not pytest_found and pytest.returncode != 0:
        pytest_map = {}
        pytest_error = (pytest.stderr or pytest.stdout or "pytest failed")[-800:]
    else:
        pytest_map = _status_from_map(PYTEST_NAMES, pytest_found, "pytest")

    direct = _json_tool([sys.executable, "qa/cross/direct_checks.py"], 120)
    rules = _json_tool([sys.executable, "qa/cross/api_rules.py"], 30)
    security = _json_tool([sys.executable, "qa/cross/security_scan.py"], 30)
    node = _json_tool(["node", "qa/cross/ui_checks.mjs"], 30)
    rg = _json_tool([sys.executable, "qa/cross/rg_rules.py"], 60)

    gradle_started = time.time()
    gradle_error = ""
    try:
        gradle = _run(
            ["./gradlew", "test", "--offline", "--tests", "com.mido.scan.ScanControllerTest"],
            ROOT / "back", 180,
        )
    except subprocess.TimeoutExpired:
        gradle = subprocess.CompletedProcess(
            args=["./gradlew", "test", "--offline"], returncode=1, stdout="", stderr="offline timeout",
        )
    need_online = (
        gradle.returncode != 0
        and (
            "No cached version" in (gradle.stdout + gradle.stderr)
            or "offline timeout" in (gradle.stderr or "")
            or "TIMEOUT" in (gradle.stderr or "")
        )
    )
    if need_online:
        gradle_started = time.time()
        try:
            gradle = _run(
                ["./gradlew", "test", "--tests", "com.mido.scan.ScanControllerTest"],
                ROOT / "back", 420,
            )
        except subprocess.TimeoutExpired as exc:
            gradle = subprocess.CompletedProcess(
                args=["./gradlew", "test"], returncode=1, stdout="", stderr=f"gradle timeout: {exc}",
            )
    report = ROOT / "back" / "build" / "test-results" / "test" / "TEST-com.mido.scan.ScanControllerTest.xml"
    fresh = report.exists() and report.stat().st_mtime >= gradle_started - 2
    gradle_found = _junit(report) if gradle.returncode == 0 or fresh else {}
    if gradle.returncode != 0 and not gradle_found:
        gradle_error = (gradle.stderr or gradle.stdout or "gradle failed")[-800:]
        gradle_map = {tc_id: _missing(tc_id, "ERROR", gradle_error) for tc_id in GRADLE_NAMES.values()}
    else:
        gradle_map = _status_from_map(GRADLE_NAMES, gradle_found, "gradle")

    tsc = _run(["npx", "tsc", "--noEmit"], ROOT / "front", 180)
    vite = _run(["npx", "vite", "build"], ROOT / "front", 180)
    compose = _json_tool([sys.executable, "qa/cross/compose_checks.py"], 30)
    dockerfiles = _json_tool([sys.executable, "qa/cross/dockerfile_checks.py"], 30)
    smoke = _json_tool([sys.executable, "qa/cross/http_smoke.py"], 30)

    def _cmd(tc_id: str, proc: subprocess.CompletedProcess, label: str) -> dict:
        status = "PASS" if proc.returncode == 0 else "FAIL"
        tail = " ".join((proc.stdout or proc.stderr or "").split())[-180:]
        return {
            "id": tc_id, "status": status, "expected": "exit 0",
            "actual": f"exit {proc.returncode}",
            "evidence": f"{label} exit {proc.returncode} {tail}".strip(),
            "file": "front/package.json", "function": label, "line": "UNKNOWN",
            "error": "" if status == "PASS" else tail, "cause": "" if status == "PASS" else tail,
            "input": label,
        }

    buckets = {
        "pytest": pytest_map,
        "direct": _index(direct),
        "rules": _index(rules),
        "gradle": gradle_map,
        "security": _index(security),
        "node": _index(node),
        "rg": _index(rg),
        "tsc": {"REG-FRONT": _cmd("REG-FRONT", tsc, "tsc --noEmit")},
        "vite": {"REG-FRONT": _cmd("REG-FRONT", vite, "vite build")},
        "compose": _index(compose),
        "dockerfiles": _index(dockerfiles),
        "smoke_front": {},
        "smoke_back": {},
        "none": {},
    }
    smoke_idx = _index(smoke)
    if "INFRA-SMOKE-FRONT" in smoke_idx:
        buckets["smoke_front"]["INFRA-SMOKE"] = {**smoke_idx["INFRA-SMOKE-FRONT"], "id": "INFRA-SMOKE"}
    if "INFRA-SMOKE-BACK" in smoke_idx:
        buckets["smoke_back"]["INFRA-SMOKE"] = {**smoke_idx["INFRA-SMOKE-BACK"], "id": "INFRA-SMOKE"}
    for label, payload in (("compose", compose), ("dockerfiles", dockerfiles), ("smoke", smoke)):
        if payload.get("_error") and not payload.get("cases"):
            buckets[label + "_error"] = payload["_error"]
            if label in ("compose", "dockerfiles"):
                buckets[label] = {}

    if pytest_error:
        buckets["pytest_error"] = pytest_error
    if direct.get("_error") and not direct.get("cases"):
        buckets["direct"] = {}
        buckets["direct_error"] = direct["_error"]
    for label, payload in (("security", security), ("node", node), ("rg", rg), ("rules", rules)):
        if payload.get("_error") and not payload.get("cases"):
            buckets[label + "_error"] = payload["_error"]
            buckets[label] = {}

    results: list[CaseResult] = []
    risks: list[RiskNote] = []
    sections = _section_map()
    for row in CASES:
        (tc_id, test_type, feature, mode, required, severity, likelihood, impact,
         recommendation, issue, purpose, repro, tool_a, tool_b, source_a, source_b) = row
        if source_a == "pytest" and buckets.get("pytest_error") and tc_id not in buckets["pytest"]:
            left = _missing(tc_id, "ERROR", buckets["pytest_error"])
        elif source_a + "_error" in buckets and tc_id not in buckets.get(source_a, {}):
            left = _missing(tc_id, "ERROR", buckets[source_a + "_error"])
        else:
            left = _bucket(source_a, buckets, tc_id)
        if source_b + "_error" in buckets and tc_id not in buckets.get(source_b, {}):
            right = _missing(tc_id, "ERROR", buckets[source_b + "_error"])
        else:
            right = _bucket(source_b, buckets, tc_id)
        final = _decide(mode, left["status"], right["status"])
        file, function, line = _loc(left, right)
        evidence = (
            f"A[{left['status']}] {left.get('evidence','')} || B[{right['status']}] {right.get('evidence','')}"
        )[:500]
        actual = f"A:{left.get('actual','')} / B:{right.get('actual','')}"
        expected = left.get("expected") or right.get("expected") or purpose
        cause = " ".join(part for part in (left.get("cause") or "", right.get("cause") or "") if part)
        if final == "ERROR" and left["status"] != right["status"] and mode == "agree":
            cause = (cause + " 두 도구 결과가 달라 ERROR.").strip()
        risk = f"RISK-{tc_id}" if severity and final in {"FAIL", "ERROR"} else "NONE"
        section = sections.get(tc_id) or feature
        results.append(CaseResult(
            tc_id=tc_id, feature=feature, test_type=test_type,
            tool_a=tool_a, tool_a_result=left["status"],
            tool_b=tool_b, tool_b_result=right["status"],
            final_status=final, file=file, function=function, line=line,
            issue_id=issue or "NONE", risk_id=risk, evidence=evidence,
            purpose=purpose, expected=expected, actual=actual, repro=repro,
            cause=cause, error=left.get("error") or right.get("error") or "",
            input_value=left.get("input") or right.get("input") or "",
            required=required, severity=severity,
            section=section,
        ))
        if risk != "NONE":
            risks.append(RiskNote(
                risk_id=risk, test_type=test_type, severity=severity,
                likelihood=likelihood, impact=impact, recommendation=recommendation,
                tc_id=tc_id, file=file, function=function, line=line, issue_id=issue or "NONE",
                detail=cause or evidence[:400],
                section=section,
            ))

    risks.append(RiskNote(
        risk_id="RISK-API-TOOLB-NO-SOCKET",
        test_type="api",
        severity="MEDIUM",
        likelihood="매 실행. 도구 B는 HTTP를 열지 않는다.",
        impact="MockMvc만 본 상태 코드는 교차 검증된 PASS가 아니다.",
        recommendation="두 번째 HTTP 도구를 붙이기 전에는 Gradle 전용 TC를 PASS로 올리지 않는다.",
        tc_id="API-CREATE",
        file="back/src/test/java/com/mido/scan/ScanControllerTest.java",
        function="createAndGet",
        line="UNKNOWN",
        section="scan_create_get",
        detail="api_rules.py는 @NotBlank/@Size만 재구현한다. 201/404/500은 이번 도구 B가 관찰하지 않았다.",
    ))
    risks.append(RiskNote(
        risk_id="RISK-COVERAGE-GAP",
        test_type="regression",
        severity="MEDIUM",
        likelihood="이 러너가 Playwright E2E·k6 부하·라이브 NVD를 실행하지 않는다.",
        impact="브라우저 클릭·부하 수치·라이브 API는 이번 RUN의 PASS가 아니다.",
        recommendation="해당 검사를 실제로 실행하기 전에는 날짜 폴더를 만들지 않는다.",
        tc_id="NONE",
        section="coverage_gap",
        detail="V3 목표 도구 중 미도입 항목은 별도 RISK로 남긴다.",
    ))
    risks.append(RiskNote(
        risk_id="RISK-V3-TOOL-GAP",
        test_type="security",
        severity="HIGH",
        likelihood="CodeQL·Semgrep·Playwright·Schemathesis·Testcontainers 미연결.",
        impact="V3 권장 이중 경로 일부가 현재 게이트에 없다. 정적 대체 경로만 실행 중.",
        recommendation="CI에 CodeQL/Semgrep, web에 Playwright+OpenAPI 검사를 단계적으로 연결한다.",
        tc_id="NONE",
        section="tooling_gap",
        detail="현재 03_security_quality는 security_scan+ui/rg, 02_web_api는 MockMvc+api_rules.",
        status="OPEN",
    ))

    record = RunRecord(
        run_id=current, executed_at=started, git_commit=commit, cases=results, risks=risks,
    )
    written = write_run(ROOT, record)
    # Sync qa/input/testcases.tsv status columns from this dual-verify run.
    try:
        import csv
        from pathlib import Path as _P
        tsv_path = ROOT / "qa" / "input" / "testcases.tsv"
        if tsv_path.exists():
            with tsv_path.open("r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f, delimiter="\t")
                fields = list(reader.fieldnames or [])
                rows = list(reader)
            by_id = {c.tc_id: c for c in results}
            for row in rows:
                case = by_id.get((row.get("TC_ID") or "").strip())
                if not case:
                    continue
                row["상태"] = case.final_status
                row["최근실행"] = started
                row["상세"] = (
                    f"A[{case.tool_a_result}] {case.tool_a} || "
                    f"B[{case.tool_b_result}] {case.tool_b} | {case.evidence}"
                )[:500]
                row["실행명령"] = f"{case.tool_a} || {case.tool_b}"
                row["종료코드"] = "0" if case.final_status == "PASS" else "1"
            with tsv_path.open("w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
                writer.writeheader()
                writer.writerows(rows)
            written.append(tsv_path)
    except OSError as exc:
        print(f"NOTICE: could not sync input TSV: {exc}", file=sys.stderr)
    blocking = [
        case.tc_id for case in results
        if case.required and case.final_status in {"FAIL", "ERROR", "BLOCKED", "NOT_RUN"}
    ]
    high = [risk.risk_id for risk in risks if risk.severity in {"HIGH", "CRITICAL"} and risk.status == "OPEN"]
    code = 1 if blocking or high else 0
    stamp = {
        "run_id": current,
        "executed_at": started,
        "git_commit": commit,
        "exit_code": code,
        "blocking": blocking,
        "high_open": high,
    }
    from qa.layout import ensure_area_tree

    ensure_area_tree(ROOT)
    stamp_path = ROOT / "qa" / "results" / ".last_run"
    stamp_path.parent.mkdir(parents=True, exist_ok=True)
    stamp_path.write_text(json.dumps(stamp, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    counts: dict[str, int] = {}
    for case in results:
        counts[case.final_status] = counts.get(case.final_status, 0) + 1
    print(f"RUN_ID {current} exit {code} commit {commit}")
    print("status " + " ".join(f"{key}={counts[key]}" for key in sorted(counts)))
    if blocking:
        print("blocking " + ", ".join(blocking))
    if high:
        print("high " + ", ".join(high))
    print("results " + ", ".join(str(path.relative_to(ROOT)) for path in written[:8]) + " ...")
    return code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"QA runner ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
