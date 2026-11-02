"""QA 실행 결과를 4영역/기능/날짜 폴더에 기록한다. 당일 스냅샷 5개 파일을 갱신한다."""
from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from qa.layout import execution_log_path, master_path, normalize_area, result_dir, safe_name

MASTER_HEADER = [
    "TC_ID",
    "area",
    "section",
    "feature",
    "type",
    "check_a",
    "check_a_result",
    "check_b",
    "check_b_result",
    "final_status",
    "expected",
    "actual",
    "evidence",
    "file",
    "function",
    "line",
    "issue_id",
    "risk_id",
    "executed_at",
    "run_id",
    "git_commit",
]

SEOUL = ZoneInfo("Asia/Seoul")
RESULTS_HEADER = [
    "RUN_ID",
    "TC_ID",
    "FEATURE_ID",
    "AREA",
    "SECTION",
    "TOOL_A",
    "TOOL_A_RESULT",
    "TOOL_B",
    "TOOL_B_RESULT",
    "FINAL_STATUS",
    "EXPECTED",
    "ACTUAL",
    "EVIDENCE",
    "GIT_COMMIT",
    "FILE",
    "FUNCTION",
    "LINE",
    "ISSUE_ID",
    "RISK_ID",
    "EXECUTED_AT",
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
    area: str = ""
    section: str = ""

    def __post_init__(self) -> None:
        for name in ("tool_a_result", "tool_b_result", "final_status"):
            value = getattr(self, name)
            if value not in STATUSES:
                raise ValueError(f"{self.tc_id} {name}={value}")
        if not self.area:
            self.area = normalize_area(self.test_type)
        else:
            self.area = normalize_area(self.area)
        if not self.section:
            self.section = self.feature or self.test_type


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
    area: str = ""
    section: str = ""

    def __post_init__(self) -> None:
        if not self.area:
            self.area = normalize_area(self.test_type)
        else:
            self.area = normalize_area(self.area)
        if not self.section:
            self.section = self.test_type


@dataclass
class RunRecord:
    run_id: str
    executed_at: str
    git_commit: str
    cases: list[CaseResult] = field(default_factory=list)
    risks: list[RiskNote] = field(default_factory=list)


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body if body.endswith("\n") else body + "\n", encoding="utf-8")


def _write_summary(path: Path, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(RESULTS_HEADER)
        writer.writerows(rows)


def _try_sheet(path: Path, rows: list[dict], title: str, date: str) -> None:
    try:
        import openpyxl
        from openpyxl.styles import Alignment, Font, PatternFill
    except ImportError:
        return
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "detail"[:31]
    headers = RESULTS_HEADER
    ws["A1"] = title
    ws["A1"].font = Font(bold=True, color="FFFFFF", size=14)
    ws["A1"].fill = PatternFill("solid", fgColor="17324E")
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
    ws["A2"] = f"기준일 {date} | 이중 검증 결과 | 미실행은 PASS가 아님"
    for col, header in enumerate(headers, 1):
        cell_ref = ws.cell(3, col, header)
        cell_ref.fill = PatternFill("solid", fgColor="255E79")
        cell_ref.font = Font(bold=True, color="FFFFFF")
        cell_ref.alignment = Alignment(horizontal="center")
    for r_idx, row in enumerate(rows, 4):
        for c_idx, key in enumerate(headers, 1):
            ws.cell(r_idx, c_idx, str(row.get(key, "") or ""))
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def _append_tsv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not path.exists() or path.stat().st_size == 0
    mode = "w" if new_file else "a"
    encoding = "utf-8-sig" if new_file else "utf-8"
    with path.open(mode, encoding=encoding, newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        if new_file:
            writer.writerow(header)
        writer.writerows(rows)


def write_master_xlsx(root: Path, record: RunRecord) -> Path:
    """qa/master_test_sheet.xlsx — single root aggregate Excel (latest snapshot)."""
    path = master_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    legacy = root / "qa" / "master_test_sheet.tsv"
    if legacy.exists():
        legacy.unlink()
    try:
        import openpyxl
        from openpyxl.styles import Alignment, Font, PatternFill
    except ImportError:
        # openpyxl 없으면 히스토리에 스냅샷 TSV만 (루트 Excel 중복 생성 안 함)
        snap = root / "qa" / "history" / "master_snapshot.tsv"
        with snap.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
            writer.writerow(MASTER_HEADER)
            for case in record.cases:
                writer.writerow([
                    cell(case.tc_id), cell(case.area), cell(safe_name(case.section)), cell(case.feature),
                    cell(case.test_type), cell(case.tool_a), cell(case.tool_a_result), cell(case.tool_b),
                    cell(case.tool_b_result), cell(case.final_status), cell(case.expected), cell(case.actual),
                    cell(case.evidence), cell(case.file), cell(case.function), cell(case.line),
                    cell(case.issue_id), cell(case.risk_id), cell(record.executed_at), cell(record.run_id),
                    cell(record.git_commit),
                ])
        return snap
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "master"
    ws["A1"] = "Master QA test sheet"
    ws["A1"].font = Font(bold=True, color="FFFFFF", size=14)
    ws["A1"].fill = PatternFill("solid", fgColor="17324E")
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(MASTER_HEADER))
    ws["A2"] = f"RUN {record.run_id} | {record.executed_at} | commit {record.git_commit} | 미실행은 PASS 아님"
    for col, header in enumerate(MASTER_HEADER, 1):
        c = ws.cell(3, col, header)
        c.fill = PatternFill("solid", fgColor="255E79")
        c.font = Font(bold=True, color="FFFFFF")
        c.alignment = Alignment(horizontal="center")
    for r_idx, case in enumerate(record.cases, 4):
        vals = [
            case.tc_id, case.area, safe_name(case.section), case.feature, case.test_type,
            case.tool_a, case.tool_a_result, case.tool_b, case.tool_b_result, case.final_status,
            case.expected, case.actual, case.evidence, case.file, case.function, case.line,
            case.issue_id, case.risk_id, record.executed_at, record.run_id, record.git_commit,
        ]
        for c_idx, val in enumerate(vals, 1):
            ws.cell(r_idx, c_idx, cell(val))
    wb.save(path)
    return path


def append_execution_log(root: Path, record: RunRecord) -> Path:
    path = execution_log_path(root)
    rows = []
    for case in record.cases:
        rows.append([
            cell(record.run_id), cell(case.tc_id), cell(case.feature), cell(case.area),
            cell(safe_name(case.section)), cell(case.tool_a), cell(case.tool_a_result),
            cell(case.tool_b), cell(case.tool_b_result), cell(case.final_status),
            cell(case.expected), cell(case.actual), cell(case.evidence), cell(record.git_commit),
            cell(case.file), cell(case.function), cell(case.line), cell(case.issue_id),
            cell(case.risk_id), cell(record.executed_at),
        ])
    _append_tsv(path, RESULTS_HEADER, rows)
    return path


def write_run(root: Path, record: RunRecord) -> list[Path]:
    """Day snapshot MD/XLSX + append-only results.tsv and execution_log.tsv."""
    day = record.executed_at[:10]
    written: list[Path] = []
    written.append(write_master_xlsx(root, record))
    written.append(append_execution_log(root, record))
    groups: dict[tuple[str, str], dict] = defaultdict(lambda: {"cases": [], "risks": []})

    for case in record.cases:
        key = (case.area, safe_name(case.section))
        groups[key]["cases"].append(case)
    for risk in record.risks:
        key = (risk.area, safe_name(risk.section or risk.test_type))
        groups[key]["risks"].append(risk)

    history_dir = root / "qa" / "history" / day
    history_dir.mkdir(parents=True, exist_ok=True)
    history_path = history_dir / f"{record.run_id}.jsonl"
    with history_path.open("w", encoding="utf-8") as hist:
        import json

        for case in record.cases:
            hist.write(json.dumps({
                "run_id": record.run_id,
                "tc_id": case.tc_id,
                "area": case.area,
                "section": case.section,
                "status": case.final_status,
                "tool_a": case.tool_a,
                "tool_a_result": case.tool_a_result,
                "tool_b": case.tool_b,
                "tool_b_result": case.tool_b_result,
                "stamp": record.executed_at,
            }, ensure_ascii=False) + "\n")
    written.append(history_path)

    for (area, section_key), payload in sorted(groups.items()):
        cases: list[CaseResult] = payload["cases"]
        risks: list[RiskNote] = payload["risks"]
        section_label = cases[0].section if cases else (risks[0].section if risks else section_key)
        folder = result_dir(root, area, section_label, day)

        pass_cases = [c for c in cases if c.final_status == "PASS"]
        fail_cases = [c for c in cases if c.final_status in {"FAIL", "ERROR"}]
        risk_or_skip = [c for c in cases if c.final_status in {"NOT_RUN", "BLOCKED", "SKIPPED"}]

        pass_lines = [
            f"# {area} / {section_label} PASS",
            "",
            f"RUN: {record.run_id} | {record.executed_at} | commit {record.git_commit}",
            f"PASS {len(pass_cases)} / FAIL {len(fail_cases)} / OTHER {len(risk_or_skip)}",
            "",
        ]
        if not pass_cases:
            pass_lines.append("이번 RUN의 PASS는 없다.")
        for case in pass_cases:
            pass_lines += [
                f"## {case.tc_id} {case.feature}",
                "",
                f"- 목적: {cell(case.purpose)}",
                f"- 도구 A: {case.tool_a} / {case.tool_a_result}",
                f"- 도구 B: {case.tool_b} / {case.tool_b_result}",
                f"- 기대: {cell(case.expected)}",
                f"- 실제: {cell(case.actual)}",
                f"- 근거: {cell(case.evidence)}",
                f"- 위치: {cell(case.file)} {cell(case.function)}:{cell(case.line)}",
                "",
            ]
        _write_text(folder / "pass.md", "\n".join(pass_lines))
        written.append(folder / "pass.md")

        fail_lines = [
            f"# {area} / {section_label} FAIL",
            "",
            f"RUN: {record.run_id} | {record.executed_at} | commit {record.git_commit}",
            "",
        ]
        if not fail_cases:
            fail_lines.append("이번 RUN의 FAIL/ERROR는 없다.")
        for case in fail_cases:
            fail_lines += [
                f"## {case.tc_id} {case.feature}",
                "",
                f"- 최종 상태: {case.final_status}",
                f"- 입력값: {cell(case.input_value)}",
                f"- 오류 메시지: {cell(case.error)}",
                f"- 재현: {cell(case.repro)}",
                f"- 기대: {cell(case.expected)}",
                f"- 실제: {cell(case.actual)}",
                f"- 도구 A: {case.tool_a} / {case.tool_a_result}",
                f"- 도구 B: {case.tool_b} / {case.tool_b_result}",
                f"- 근거: {cell(case.evidence)}",
                f"- 파일: {cell(case.file)}",
                f"- 함수: {cell(case.function)}",
                f"- 줄: {cell(case.line)}",
                f"- 원인: {cell(case.cause)}",
                "- 수정 위치: UNKNOWN",
                "- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.",
                f"- GIT: {record.git_commit} / ISSUE: {case.issue_id} / RISK: {case.risk_id}",
                "",
            ]
        _write_text(folder / "fail.md", "\n".join(fail_lines))
        written.append(folder / "fail.md")

        risk_lines = [
            f"# {area} / {section_label} RISK",
            "",
            f"RUN: {record.run_id} | {record.executed_at} | commit {record.git_commit}",
            "",
            "## 이중 검증·미실행 안내",
            "- 도구 A/B 중 하나만 실행한 결과는 PASS가 아니다.",
            "- NOT_RUN·BLOCKED·SKIPPED는 배포 게이트 통과 근거로 쓰지 않는다.",
            "",
        ]
        if risk_or_skip:
            risk_lines.append("## 미실행·차단 TC")
            for case in risk_or_skip:
                risk_lines += [
                    f"### {case.tc_id} ({case.final_status})",
                    f"- 도구 A: {case.tool_a} / {case.tool_a_result}",
                    f"- 도구 B: {case.tool_b} / {case.tool_b_result}",
                    f"- 근거: {cell(case.evidence)}",
                    "",
                ]
        if risks:
            risk_lines.append("## OPEN RISK")
            for risk in risks:
                risk_lines += [
                    f"### {risk.risk_id}",
                    "",
                    f"- 연결 TC: {risk.tc_id}",
                    f"- 심각도: {risk.severity}",
                    f"- 발생 가능성: {cell(risk.likelihood)}",
                    f"- 영향: {cell(risk.impact)}",
                    f"- 권장 조치: {cell(risk.recommendation)}",
                    f"- 처리 상태: {risk.status}",
                    f"- 위치: {cell(risk.file)} {cell(risk.function)}:{cell(risk.line)}",
                    f"- ISSUE: {risk.issue_id}",
                    f"- 내용: {cell(risk.detail)}",
                    "",
                ]
        if not risks and not risk_or_skip:
            risk_lines.append("이번 RUN에서 새로 연 RISK와 미실행 TC는 없다.")
        _write_text(folder / "risk.md", "\n".join(risk_lines))
        written.append(folder / "risk.md")

        result_rows: list[list[str]] = []
        sheet_rows: list[dict] = []
        for case in cases:
            result_rows.append([
                cell(record.run_id), cell(case.tc_id), cell(case.feature), cell(case.area),
                cell(safe_name(case.section)), cell(case.tool_a), cell(case.tool_a_result),
                cell(case.tool_b), cell(case.tool_b_result), cell(case.final_status),
                cell(case.expected), cell(case.actual), cell(case.evidence), cell(record.git_commit),
                cell(case.file), cell(case.function), cell(case.line), cell(case.issue_id),
                cell(case.risk_id), cell(record.executed_at),
            ])
            sheet_rows.append({
                "RUN_ID": record.run_id,
                "TC_ID": case.tc_id,
                "FEATURE_ID": case.feature,
                "AREA": case.area,
                "SECTION": safe_name(case.section),
                "TOOL_A": case.tool_a,
                "TOOL_A_RESULT": case.tool_a_result,
                "TOOL_B": case.tool_b,
                "TOOL_B_RESULT": case.tool_b_result,
                "FINAL_STATUS": case.final_status,
                "EXPECTED": case.expected,
                "ACTUAL": case.actual,
                "EVIDENCE": case.evidence,
                "GIT_COMMIT": record.git_commit,
                "FILE": case.file,
                "FUNCTION": case.function,
                "LINE": case.line,
                "ISSUE_ID": case.issue_id,
                "RISK_ID": case.risk_id,
                "EXECUTED_AT": record.executed_at,
            })
        # append-only results.tsv (V3); remove legacy summary.tsv if present
        legacy_summary = folder / "summary.tsv"
        if legacy_summary.exists():
            legacy_summary.unlink()
        _append_tsv(folder / "results.tsv", RESULTS_HEADER, result_rows)
        written.append(folder / "results.tsv")
        _try_sheet(
            folder / "test_sheet.xlsx",
            sheet_rows,
            f"{area} / {safe_name(section_label)} detail",
            day,
        )
        if (folder / "test_sheet.xlsx").exists():
            written.append(folder / "test_sheet.xlsx")

    return written
