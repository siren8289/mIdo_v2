"""QA 실행 결과를 날짜 폴더에 누적한다. 기존 파일은 덮어쓰지 않는다."""
import csv
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

SEOUL = ZoneInfo("Asia/Seoul")
HEADER = [
    "RUN_ID",
    "TC_ID",
    "EXECUTED_AT",
    "FEATURE",
    "TEST_TYPE",
    "TOOL_A",
    "TOOL_A_RESULT",
    "TOOL_B",
    "TOOL_B_RESULT",
    "FINAL_STATUS",
    "GIT_COMMIT",
    "FILE",
    "FUNCTION",
    "LINE",
    "ISSUE_ID",
    "RISK_ID",
    "EVIDENCE",
]
STATUSES = {"PASS", "FAIL", "BLOCKED", "ERROR", "NOT_RUN", "SKIPPED"}


def now_seoul() -> datetime:
    return datetime.now(SEOUL)


def run_id(moment: datetime) -> str:
    return moment.strftime("RUN-%Y%m%d-%H%M%S")


def cell(value: object) -> str:
    text = "UNKNOWN" if value is None or value == "" else str(value)
    text = text.replace("\t", " ").replace("\r", " ").replace("\n", " ").strip()
    if text[:1] in "=+-@":
        text = "'" + text
    return text


@dataclass
class CaseResult:
    tc_id: str
    feature: str
    test_type: str
    tool_a: str
    tool_a_result: str
    tool_b: str
    tool_b_result: str
    final_status: str
    file: str = "UNKNOWN"
    function: str = "UNKNOWN"
    line: str = "UNKNOWN"
    issue_id: str = "NONE"
    risk_id: str = "NONE"
    evidence: str = ""
    purpose: str = ""
    expected: str = ""
    actual: str = ""
    repro: str = ""
    cause: str = ""
    error: str = ""
    input_value: str = ""
    required: bool = True
    severity: str = ""
    likelihood: str = ""
    impact: str = ""
    recommendation: str = ""
    risk_only: bool = False

    def __post_init__(self) -> None:
        for name in ("tool_a_result", "tool_b_result", "final_status"):
            value = getattr(self, name)
            if value not in STATUSES:
                raise ValueError(f"{self.tc_id} {name}={value}")


@dataclass
class RiskNote:
    risk_id: str
    test_type: str
    severity: str
    likelihood: str
    impact: str
    recommendation: str
    status: str = "OPEN"
    tc_id: str = "NONE"
    file: str = "UNKNOWN"
    function: str = "UNKNOWN"
    line: str = "UNKNOWN"
    issue_id: str = "NONE"
    detail: str = ""


@dataclass
class RunRecord:
    run_id: str
    executed_at: str
    git_commit: str
    cases: list[CaseResult] = field(default_factory=list)
    risks: list[RiskNote] = field(default_factory=list)


def _append_text(path: Path, title: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.stat().st_size == 0:
        path.write_text(f"# {title}\n\n", encoding="utf-8")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(body)
        if not body.endswith("\n"):
            handle.write("\n")


def _append_tsv(path: Path, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not path.exists() or path.stat().st_size == 0
    mode = "w" if new_file else "a"
    encoding = "utf-8-sig" if new_file else "utf-8"
    with path.open(mode, encoding=encoding, newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        if new_file:
            writer.writerow(HEADER)
        writer.writerows(rows)


def write_run(root: Path, record: RunRecord) -> list[Path]:
    """실행한 테스트 종류만 날짜 폴더를 만들고 RUN_ID 문단을 덧붙인다."""
    moment = datetime.strptime(record.executed_at[:19], "%Y-%m-%dT%H:%M:%S")
    day = record.executed_at[:10]
    written: list[Path] = []
    by_type: dict[str, list[CaseResult]] = {}
    for case in record.cases:
        by_type.setdefault(case.test_type, []).append(case)
    risk_by_type: dict[str, list[RiskNote]] = {}
    for risk in record.risks:
        risk_by_type.setdefault(risk.test_type, []).append(risk)

    types = sorted(set(by_type) | set(risk_by_type))
    for test_type in types:
        folder = root / "qa" / "reports" / test_type / day
        cases = by_type.get(test_type, [])
        risks = risk_by_type.get(test_type, [])
        pass_body = [f"## {record.run_id}\n"]
        fail_body = [f"## {record.run_id}\n"]
        pass_count = 0
        fail_count = 0
        for case in cases:
            if case.final_status == "PASS":
                pass_count += 1
                pass_body.append(
                    f"### {case.tc_id} {case.feature}\n\n"
                    f"- 목적: {cell(case.purpose)}\n"
                    f"- 도구 A: {case.tool_a} / {case.tool_a_result}\n"
                    f"- 도구 B: {case.tool_b} / {case.tool_b_result}\n"
                    f"- 기대: {cell(case.expected)}\n"
                    f"- 실제: {cell(case.actual)}\n"
                    f"- 근거: {cell(case.evidence)}\n"
                    f"- 위치: {cell(case.file)} {cell(case.function)}:{cell(case.line)}\n"
                    f"- 시각: {record.executed_at} / 커밋: {record.git_commit}\n"
                )
            elif case.final_status in {"FAIL", "ERROR"}:
                fail_count += 1
                fail_body.append(
                    f"### {case.tc_id} {case.feature}\n\n"
                    f"- 최종 상태: {case.final_status}\n"
                    f"- 입력값: {cell(case.input_value)}\n"
                    f"- 오류 메시지: {cell(case.error)}\n"
                    f"- 재현: {cell(case.repro)}\n"
                    f"- 기대: {cell(case.expected)}\n"
                    f"- 실제: {cell(case.actual)}\n"
                    f"- 도구 A: {case.tool_a} / {case.tool_a_result}\n"
                    f"- 도구 B: {case.tool_b} / {case.tool_b_result}\n"
                    f"- 근거: {cell(case.evidence)}\n"
                    f"- 파일: {cell(case.file)}\n"
                    f"- 함수: {cell(case.function)}\n"
                    f"- 줄: {cell(case.line)}\n"
                    f"- 원인: {cell(case.cause)}\n"
                    f"- 수정 위치: UNKNOWN\n"
                    f"- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.\n"
                    f"- GIT: {record.git_commit} / ISSUE: {case.issue_id} / RISK: {case.risk_id}\n"
                    f"- 시각: {record.executed_at}\n"
                )
        if pass_count:
            path = folder / "pass.md"
            _append_text(path, f"{test_type} PASS", "\n".join(pass_body) + "\n")
            written.append(path)
        elif not (folder / "pass.md").exists():
            _append_text(folder / "pass.md", f"{test_type} PASS", f"## {record.run_id}\n\n이번 RUN의 PASS는 없다.\n")
            written.append(folder / "pass.md")
        else:
            _append_text(folder / "pass.md", f"{test_type} PASS", f"## {record.run_id}\n\n이번 RUN의 PASS는 없다.\n")
            written.append(folder / "pass.md")
        if fail_count:
            path = folder / "fail.md"
            _append_text(path, f"{test_type} FAIL", "\n".join(fail_body) + "\n")
            written.append(path)
        elif not (folder / "fail.md").exists():
            _append_text(folder / "fail.md", f"{test_type} FAIL", f"## {record.run_id}\n\n이번 RUN의 FAIL/ERROR는 없다.\n")
            written.append(folder / "fail.md")
        else:
            _append_text(folder / "fail.md", f"{test_type} FAIL", f"## {record.run_id}\n\n이번 RUN의 FAIL/ERROR는 없다.\n")
            written.append(folder / "fail.md")

        risk_lines = [f"## {record.run_id}\n"]
        if risks:
            for risk in risks:
                risk_lines.append(
                    f"### {risk.risk_id}\n\n"
                    f"- 연결 TC: {risk.tc_id}\n"
                    f"- 심각도: {risk.severity}\n"
                    f"- 발생 가능성: {cell(risk.likelihood)}\n"
                    f"- 영향: {cell(risk.impact)}\n"
                    f"- 권장 조치: {cell(risk.recommendation)}\n"
                    f"- 처리 상태: {risk.status}\n"
                    f"- 위치: {cell(risk.file)} {cell(risk.function)}:{cell(risk.line)}\n"
                    f"- ISSUE: {risk.issue_id}\n"
                    f"- 내용: {cell(risk.detail)}\n"
                    f"- 시각: {record.executed_at} / 커밋: {record.git_commit}\n"
                )
        else:
            risk_lines.append("이번 RUN에서 새로 연 RISK는 없다.\n")
        risk_path = folder / "risk.md"
        _append_text(risk_path, f"{test_type} RISK", "\n".join(risk_lines) + "\n")
        written.append(risk_path)

        rows = []
        for case in cases:
            rows.append([
                cell(record.run_id),
                cell(case.tc_id),
                cell(record.executed_at),
                cell(case.feature),
                cell(case.test_type),
                cell(case.tool_a),
                cell(case.tool_a_result),
                cell(case.tool_b),
                cell(case.tool_b_result),
                cell(case.final_status),
                cell(record.git_commit),
                cell(case.file),
                cell(case.function),
                cell(case.line),
                cell(case.issue_id),
                cell(case.risk_id),
                cell(case.evidence),
            ])
        tsv = folder / "results.tsv"
        _append_tsv(tsv, rows)
        written.append(tsv)
    return written
