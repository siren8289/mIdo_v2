#!/usr/bin/env python3
"""Refresh qa/master_test_sheet.xlsx and per-section test_sheet.xlsx from TSV."""
import argparse
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from run_qa import ROOT, load_cases, safe_section
from qa.layout import master_path, result_dir

HEADERS = [
    'TC_ID', 'AREA', 'SECTION', 'feature', 'type', 'input', 'expected', 'test_ref',
    'priority', 'note', 'status', 'last_run', 'detail', 'command', 'exit_code',
]
KEYS = [
    'tc_id', 'area', 'section', 'feature', 'kind', 'input', 'expected', 'test_ref',
    'priority', 'memo', 'status', 'stamp', 'detail', 'command', 'exit_code',
]


def build_workbook(path: Path, records, title: str, tab_name: str, date: str) -> None:
    import openpyxl
    from openpyxl.styles import Alignment, Font, PatternFill

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = tab_name[:31]
    ws['A1'] = title
    ws['A1'].font = Font(bold=True, color='FFFFFF', size=14)
    ws['A1'].fill = PatternFill('solid', fgColor='17324E')
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(HEADERS))
    ws['A2'] = f'date {date} | source qa/input/testcases.tsv | unrun=NOT_RUN'
    for col, header in enumerate(HEADERS, 1):
        cell = ws.cell(3, col, header)
        cell.fill = PatternFill('solid', fgColor='255E79')
        cell.font = Font(bold=True, color='FFFFFF')
        cell.alignment = Alignment(horizontal='center')
    for r_idx, rec in enumerate(records, 4):
        for c_idx, key in enumerate(KEYS, 1):
            ws.cell(r_idx, c_idx, str(rec.get(key, '') or ''))
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    print(f'XLSX: {path} ({len(records)} rows)', flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--tsv', type=Path, default=ROOT / 'qa/input/testcases.tsv')
    ap.add_argument('--output', type=Path, default=ROOT / 'qa/results')
    ap.add_argument('--master', type=Path, default=None)
    ap.add_argument('--date', default=datetime.now(ZoneInfo('Asia/Seoul')).date().isoformat())
    args = ap.parse_args()
    master = args.master or master_path(ROOT)
    try:
        records, _ = load_cases(args.tsv)
        for record in records:
            src = record['raw']
            record.update(
                status=src.get('상태', '') or src.get('status', '') or 'NOT_RUN',
                stamp=src.get('최근실행', '') or '',
                detail=src.get('상세', '') or '',
                command=src.get('실행명령', '') or '',
                exit_code=src.get('종료코드', '') or '',
            )
        build_workbook(master, records, 'Master QA test sheet', 'master', args.date)
        legacy = ROOT / 'qa' / 'master_test_sheet.tsv'
        if legacy.exists():
            legacy.unlink()
        by_group = defaultdict(list)
        for rec in records:
            by_group[(rec['area'], rec['section'])].append(rec)
        for (area, section), group in by_group.items():
            dest = result_dir(ROOT, area, section, args.date) / 'test_sheet.xlsx'
            if args.output != ROOT / 'qa' / 'results':
                dest = args.output / safe_section(area) / safe_section(section) / args.date / 'test_sheet.xlsx'
            build_workbook(dest, group, f'{area}/{section} detail', 'detail', args.date)
        return 0
    except Exception as ex:  # noqa: BLE001
        print(f'EXPORT ERROR: {ex}')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
