#!/usr/bin/env python3
"""ripgrep 출력만으로 판정한다. security_scan.py / direct_checks.py 를 import 하지 않는다."""
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _rg_binary() -> str | None:
    for folder in ("/opt/homebrew/bin", "/usr/local/bin"):
        candidate = Path(folder) / "rg"
        if candidate.is_file():
            return str(candidate)
    return shutil.which("rg")


def rg(pattern: str, rel: str, extra: list[str] | None = None) -> tuple[str, list[str]]:
    binary = _rg_binary()
    if not binary:
        raise RuntimeError("rg 실행 파일을 찾지 못했다")
    args = [binary, "-n", "--no-heading", "-g", "!qa/**", "-g", "!**/node_modules/**", "-g", "!**/build/**"]
    if extra:
        args.extend(extra)
    args.extend([pattern, str(ROOT / rel)])
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode not in (0, 1):
        raise RuntimeError(proc.stderr.strip() or f"rg exit {proc.returncode}")
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    return proc.stdout, lines


def _line_no(lines: list[str]) -> str:
    """rg는 파일 하나일 때 '줄:내용', 여러 파일이면 '경로:줄:내용'을 낸다."""
    for head in lines:
        if head == "--" or head.startswith("--"):
            continue
        parts = head.split(":")
        if parts and parts[0].isdigit():
            return parts[0]
        if len(parts) >= 2 and parts[1].isdigit():
            return parts[1]
    return "UNKNOWN"


def _item(tc_id, status, rel, lines, expected, actual, evidence, cause="", input_value=""):
    return {
        "id": tc_id,
        "status": status,
        "expected": expected,
        "actual": actual,
        "evidence": evidence,
        "file": rel,
        "function": "UNKNOWN",
        "line": _line_no(lines),
        "input": input_value,
        "error": "" if status != "FAIL" else actual,
        "cause": cause,
    }


def _window(rel: str, pattern: str, after: int) -> str:
    _stdout, lines = rg(pattern, rel, ["-A", str(after)])
    return "\n".join(lines)


def main() -> None:
    cases = []

    window = _window(
        "ai/src/features/vulnerability_rag_001/harness/runtime.py",
        "def validate_tool_permission",
        12,
    )
    default_allow = "return True, None" in window
    _, lines = rg("def validate_tool_permission", "ai/src/features/vulnerability_rag_001/harness/runtime.py")
    cases.append(_item(
        "SEC-TOOL-UNKNOWN",
        "FAIL" if default_allow else "PASS",
        "ai/src/features/vulnerability_rag_001/harness/runtime.py",
        lines,
        "미등록 도구 기본 거부의 소스",
        "함수 안에 return True, None" if default_allow else "기본 허용 반환 없음",
        "rg -A 12 def validate_tool_permission",
        "금지 목록에 없으면 True를 반환한다." if default_allow else "",
        "shell_exec",
    ))

    _, deny_lines = rg("file_edit", "ai/src/features/vulnerability_rag_001/harness/runtime.py")
    cases.append(_item(
        "SEC-TOOL-DENY",
        "PASS" if deny_lines else "FAIL",
        "ai/src/features/vulnerability_rag_001/harness/runtime.py",
        deny_lines,
        "file_edit이 금지 목록에 있음",
        f"rg hits={len(deny_lines)}",
        "rg file_edit runtime.py",
        "" if deny_lines else "file_edit 문자열이 없다.",
        "file_edit",
    ))

    cvss = _window("ai/src/scoring/cvss.py", "def cvss3_base_score", 20)
    _, cvss_lines = rg("def cvss3_base_score", "ai/src/scoring/cvss.py")
    guarded = 'scope"] not in' in cvss or "scope not in" in cvss or '("U", "C")' in cvss or '{"U", "C"}' in cvss
    cases.append(_item(
        "SEC-CVSS-SX",
        "FAIL" if not guarded else "PASS",
        "ai/src/scoring/cvss.py",
        cvss_lines,
        "S는 U 또는 C만 허용하는 가드",
        "가드 없음" if not guarded else "가드 있음",
        "rg -A 20 def cvss3_base_score",
        "잘못된 scope가 KeyError 없이 점수로 이어질 수 있다." if not guarded else "",
        "S:X",
    ))

    cap = _window("ai/src/parser/dependency.py", "def parse_dependencies", 12)
    _, cap_lines = rg("def parse_dependencies", "ai/src/parser/dependency.py")
    silent = "[:MAX_DEPENDENCIES]" in cap and not any(token in cap for token in ("truncated", "생략", "잘렸"))
    cases.append(_item(
        "SEC-CAP",
        "FAIL" if silent else "PASS",
        "ai/src/parser/dependency.py",
        cap_lines,
        "50개 절단을 알리는 코드",
        "슬라이스만 있음" if silent else "절단 알림 또는 슬라이스 없음",
        "rg -A 12 def parse_dependencies",
        "MAX_DEPENDENCIES로 자르고 알림 문자열이 없다." if silent else "",
        "dependencies 51개",
    ))

    dup = _window("ai/src/parser/dependency.py", "def parse_package_json", 16)
    _, dup_lines = rg("def parse_package_json", "ai/src/parser/dependency.py")
    dup_bad = "result.append" in dup and "setdefault" not in dup and "unique" not in dup
    cases.append(_item(
        "SEC-DUP",
        "FAIL" if dup_bad else "PASS",
        "ai/src/parser/dependency.py",
        dup_lines,
        "parse_package_json이 중복을 제거",
        "append만 있고 setdefault/unique 없음" if dup_bad else "중복 제거 흔적 있음",
        "rg -A 16 def parse_package_json",
        "dependencies와 devDependencies를 그대로 이어 붙인다." if dup_bad else "",
        "lodash가 두 섹션에 있음",
    ))

    owasp = _window("ai/src/service/owasp.py", "def owasp_report", 12)
    _, owasp_lines = rg("def owasp_report", "ai/src/service/owasp.py")
    neg_bad = 'sum(item.get("cve_count"' in owasp and "max(0" not in owasp
    cases.append(_item(
        "SEC-OWASP-NEG",
        "FAIL" if neg_bad else "PASS",
        "ai/src/service/owasp.py",
        owasp_lines,
        "음수 cve_count를 합계에서 배제",
        "sum만 있고 max(0 없음" if neg_bad else "하한 있음",
        "rg -A 12 def owasp_report",
        "cve_count를 그대로 더한다." if neg_bad else "",
        '{"cve_count": -1}',
    ))
    corrupt_bad = "json.loads" in owasp and "JSONDecodeError" not in owasp
    cases.append(_item(
        "SEC-OWASP-CORRUPT",
        "FAIL" if corrupt_bad else "PASS",
        "ai/src/service/owasp.py",
        owasp_lines,
        "json.loads 예외를 잡음",
        "JSONDecodeError 처리 없음" if corrupt_bad else "예외 처리 있음",
        "rg -A 12 def owasp_report",
        "깨진 JSON이 JSONDecodeError로 전파된다." if corrupt_bad else "",
        "{",
    ))

    lookups = _window("ai/src/evidence/lookups.py", "def load_lookups", 12)
    _, lookup_lines = rg("def load_lookups", "ai/src/evidence/lookups.py")
    kev_bad = "read_text" in lookups and "FileNotFoundError" not in lookups
    cases.append(_item(
        "SEC-KEV-MISSING",
        "FAIL" if kev_bad else "PASS",
        "ai/src/evidence/lookups.py",
        lookup_lines,
        "KEV 파일 부재를 잡음",
        "read_text만 있고 FileNotFoundError 처리 없음" if kev_bad else "부재 처리 있음",
        "rg -A 12 def load_lookups",
        "없는 파일이 예외로 전파된다." if kev_bad else "",
        "없는 kev_cves.json",
    ))

    _, epss_lines = rg(r'float\(row\["epss"\]\)', "ai/src/evidence/epss.py")
    _, clamp_lines = rg(r"max\(0|0 <=|min\(1", "ai/src/evidence/epss.py")
    epss_bad = bool(epss_lines) and not clamp_lines
    cases.append(_item(
        "SEC-EPSS",
        "FAIL" if epss_bad else "PASS",
        "ai/src/evidence/epss.py",
        epss_lines or clamp_lines,
        "EPSS clamp 패턴",
        f"raw={len(epss_lines)} clamp={len(clamp_lines)}",
        "rg float(row[epss]) 와 clamp 패턴",
        "범위 제한 없이 float로 넣는다." if epss_bad else "",
        "epss=-0.1",
    ))

    _, save_lines = rg("scanRepository.save", "back/src/main/java/com/mido/scan/service/ScanService.java")
    _, guard_lines = rg(r'has\("summary"\)|isEmpty\(', "back/src/main/java/com/mido/scan/service/ScanService.java")
    empty_bad = bool(save_lines) and not guard_lines
    cases.append(_item(
        "SEC-EMPTY-AI",
        "FAIL" if empty_bad else "PASS",
        "back/src/main/java/com/mido/scan/service/ScanService.java",
        save_lines,
        "빈 AI JSON 저장 가드",
        f"save={len(save_lines)} guard={len(guard_lines)}",
        "rg scanRepository.save 와 summary 가드",
        "summary 검사 없이 save 한다." if empty_bad else "",
        "{}",
    ))

    _, sql_lines = rg(r"nativeQuery|createNativeQuery|createQuery\(", "back/src/main/java")
    cases.append(_item(
        "SEC-NO-SQL",
        "FAIL" if sql_lines else "PASS",
        "back/src/main/java",
        sql_lines,
        "native/create query 0건",
        f"hits={len(sql_lines)}",
        "rg nativeQuery|createQuery back/src/main/java",
        "query API 문자열이 있다." if sql_lines else "",
    ))

    print(json.dumps({"tool": "rg", "cases": cases}, ensure_ascii=False))


if __name__ == "__main__":
    main()
