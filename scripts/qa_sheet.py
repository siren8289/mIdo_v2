#!/usr/bin/env python3
"""Create and curate the repo-local QA master sheet (UTF-8 TSV), without changing approved expectations.

An AI agent first discovers behavior from source/tests/specs and writes a JSON draft.
This tool validates and merges that draft; it does not invent assertions or execute TSV text.
"""
import argparse
import csv
import json
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COLS = ["TC_ID", "영역", "섹션", "기능", "유형", "입력값", "예상결과", "테스트참조", "우선순위", "비고",
        "상태", "최근실행", "상세", "실행명령", "종료코드"]
SPEC_COLS = COLS[:10]
ALLOWED_TYPES = {
    "정상", "경계", "예외", "권한", "보안", "통합", "UI", "인프라", "성능", "회귀", "기타",
    "normal", "boundary", "exception", "auth", "security", "integration", "ui",
    "infra", "performance", "regression", "other",
}
ALLOWED_AREAS = {
    "01_unit_integration",
    "02_web_api",
    "03_security_quality",
    "04_infra_deploy",
}

def read_sheet(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        fields = r.fieldnames or []
        for required in SPEC_COLS[:6]:
            if required not in fields:
                raise ValueError(f"현재 QA 시트 헤더에서 {required!r} 누락; 기존 Excel 헤더를 표준화하세요")
        extra = set(fields) - set(COLS)
        if extra:
            # Preserve and write unknown columns if present; no silent data loss.
            raise ValueError(f"지원하지 않는 시트 열 {sorted(extra)}: 백업하고 규격에 맞게 변환하세요")
        records = [{key: str(row.get(key) or "") for key in COLS} for row in r if any(str(v or '').strip() for v in row.values())]
    return records

def save_sheet(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.qa-sheet-', suffix='.tmp', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=COLS, delimiter='\t', lineterminator='\n', extrasaction='ignore')
            writer.writeheader()
            writer.writerows(records)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def clean(value):
    return re.sub(r'[\t\r\n]+', ' ', str(value if value is not None else '')).strip()

def main():
    p = argparse.ArgumentParser(description='AI가 작성한 TC 초안을 프로젝트 안의 QA 시트에 추가합니다')
    p.add_argument('--sheet', type=Path, default=ROOT/'qa/input/testcases.tsv')
    p.add_argument('--draft', type=Path, help='AI-generated JSON {"cases":[{"섹션":..., ...}]}')
    p.add_argument('--init', action='store_true', help='시트가 없으면 헤더 생성')
    args = p.parse_args()
    if args.sheet.exists() and args.init and not args.draft:
        print(f'EXISTS: {args.sheet}; preserve existing rows')
        return 0
    try:
        rows = read_sheet(args.sheet)
        if args.draft:
            payload = json.loads(args.draft.read_text(encoding='utf-8-sig'))
            proposed = payload['cases'] if isinstance(payload, dict) else payload
            if not isinstance(proposed, list): raise ValueError('draft cases must be a list')
            ids = {row['TC_ID'] for row in rows}
            signature = {(row['영역'], row['섹션'], row['기능'], row['유형'], row['입력값'], row['예상결과']) for row in rows}
            added = skipped = 0
            for case in proposed:
                if not isinstance(case, dict): raise ValueError('case must be object')
                record = {k: clean(case.get(k, '')) for k in COLS}
                if not all(record.get(k) for k in ['영역', '섹션', '기능', '유형', '입력값', '예상결과']):
                    raise ValueError('draft TC requires 영역/섹션/기능/유형/입력값/예상결과; do not invent expected outcomes')
                if record['영역'] not in ALLOWED_AREAS:
                    raise ValueError(f"알 수 없는 영역: {record['영역']}; 허용={sorted(ALLOWED_AREAS)}")
                if record['유형'] not in ALLOWED_TYPES:
                    raise ValueError(f"알 수 없는 유형: {record['유형']}")
                # Avoid duplicates when AI runs the same generation again.
                sig = tuple(record[k] for k in ['영역', '섹션', '기능', '유형', '입력값', '예상결과'])
                if sig in signature:
                    skipped += 1
                    continue
                if not record['TC_ID']:
                    n = 1
                    while f'TC-{n:05d}' in ids: n += 1
                    record['TC_ID'] = f'TC-{n:05d}'
                if record['TC_ID'] in ids:
                    raise ValueError(f"기존 TC ID가 다른 내용으로 중복됨: {record['TC_ID']}; 기존 내용을 덮어쓰지 않음")
                record['테스트참조'] = record['테스트참조'] or record['TC_ID']
                record['우선순위'] = record['우선순위'] or 'P2'
                # Never import statuses from AI drafts as evidence.
                for k in COLS[10:]: record[k] = ''
                record['상태'] = 'NOT_RUN'
                record['상세'] = '실제 검증 명령이 아직 실행되지 않음'
                rows.append(record)
                ids.add(record['TC_ID'])
                signature.add(sig)
                added += 1
            print(f'DRAFT MERGE: added={added}, skipped_duplicates={skipped}')
        if not args.sheet.exists() or args.draft:
            save_sheet(args.sheet, rows)
        print(f'QA MASTER SHEET: {args.sheet} ({len(rows)} cases)')
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as ex:
        print(f'[QA SHEET ERROR] {ex}', file=sys.stderr)
        return 2

if __name__ == '__main__':
    sys.exit(main())
