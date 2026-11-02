#!/usr/bin/env python3
"""Iterative QA executor: one TC at a time -> live master sheet -> four reports per section/day.

Actual test commands must be present in a reviewed test-map.json (shell=False).
The real testing assertions must exist separately; exit code alone is not proof of coverage.
"""
import argparse
import csv
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import uuid
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from qa.layout import AREA_LABELS, normalize_area, result_dir, safe_name as safe_section  # noqa: E402

ALIASES = {
    'tc_id': ['TC_ID', 'TC ID', '테스트ID', '테스트 ID', '케이스ID', 'ID'],
    'area': ['영역', 'AREA', 'Area', '파트'],
    'section': ['섹션', 'SECTION', 'Section', '분야', '기능분류', '카테고리'],
    'feature': ['기능', '기능명', 'FEATURE', '시나리오'],
    'kind': ['유형', '테스트유형', '테스트 종류', 'TYPE'],
    'input': ['입력값', '입력', '입력 조건', 'INPUT'],
    'expected': ['예상결과', '기대결과', '예상 출력', 'EXPECTED'],
    'test_ref': ['테스트참조', 'test_ref', 'TEST_REF', '검증ID'],
    'priority': ['우선순위', 'PRIORITY'],
    'memo': ['비고', '메모', 'NOTE'],
}
STATUS_FIELDS = ['상태', '최근실행', '상세', '실행명령', '종료코드']
REPORT_COLUMNS = ['TC_ID', '영역', '섹션', '기능', '유형', '입력값', '예상결과', '테스트참조', '우선순위',
                  '상태', '상세', '명령', '종료코드', '실행일시', '검증A', '검증A결과', '검증B', '검증B결과']
TZ = ZoneInfo('Asia/Seoul')


def pick(record, key):
    return next((str(record.get(name, '') or '').strip() for name in ALIASES[key] if name in record), '')


def redact(value):
    value = re.sub(r'\x1b\[[0-9;]*m', '', str(value or ''))
    value = re.sub(r'(?i)(bearer\s+)[^\s]+', r'\1[REDACTED]', value)
    value = re.sub(r'(?i)((?:api[_-]?key|password|secret|token)\s*[:=]\s*)[^\s,;]+', r'\1[REDACTED]', value)
    return value[-2000:]


def mdesc(value):
    return (str(value).replace('|', '\\|').replace('\n', ' ').strip() or '—')


def load_cases(filename):
    with filename.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = reader.fieldnames or []
        for required in ['tc_id', 'section', 'expected']:
            if not any(alias in headers for alias in ALIASES[required]):
                raise ValueError(f'TSV 필수 열 누락: {ALIASES[required][0]}')
        cases = []
        for n, original in enumerate(reader, 2):
            if not any(str(v or '').strip() for v in original.values()):
                continue
            if None in original:
                raise ValueError(f'TSV {n}행: 헤더보다 열이 많습니다')
            item = {key: pick(original, key) for key in ALIASES}
            item['line'] = n
            item['raw'] = original
            if not all(item[k] for k in ['tc_id', 'section', 'expected']):
                raise ValueError(f'TSV {n}행: TC_ID, 섹션, 예상결과는 필수입니다')
            try:
                item['area'] = normalize_area(item['area'] or item['kind'] or item['section'])
            except ValueError as ex:
                raise ValueError(f'TSV {n}행: {ex}. 영역은 다음 중 하나여야 합니다: {", ".join(AREA_LABELS)}') from ex
            cases.append(item)
    if not cases:
        raise ValueError('TSV 데이터 행이 없습니다. 먼저 AI에 TC 시트 생성을 요청하세요')
    ids = [c['tc_id'] for c in cases]
    if len(ids) != len(set(ids)):
        raise ValueError('중복 TC_ID가 있습니다')
    folder_keys = [(c['area'], safe_section(c['section'])) for c in cases]
    if len(set(folder_keys)) != len(set((c['area'], c['section']) for c in cases)):
        raise ValueError('여러 섹션명이 동일한 폴더명으로 변환됩니다. 섹션명을 수정하세요')
    return cases, headers


def _extract_snippet(stdout: str, stderr: str, ok: bool) -> str:
    combined = (stdout if ok else (stderr or stdout)).splitlines()
    for line in reversed(combined):
        stripped = line.strip()
        if stripped.startswith('[ASSERTION]'):
            return stripped[:180]
    for line in reversed(combined):
        stripped = line.strip()
        if stripped and not stripped.startswith('---') and not stripped.startswith('Ran '):
            return stripped[:180]
    return ''


def _run_one(command, timeout, cwd, env):
    run = subprocess.run(command, cwd=cwd, shell=False, capture_output=True, text=True,
                         encoding='utf-8', errors='replace', timeout=timeout, env=env)
    out_clean = redact(run.stdout)
    err_clean = redact(run.stderr)
    snippet = _extract_snippet(out_clean, err_clean, run.returncode == 0)
    if run.returncode == 0:
        detail = f'테스트 명령 성공 ({snippet})' if snippet else '테스트 명령 성공 (TC별 assertion 검증 완료)'
        return 'PASS', detail, out_clean, err_clean, str(run.returncode)
    detail = f'테스트 명령 실패 ({snippet})' if snippet else '테스트 명령 실패'
    return 'FAIL', detail, out_clean, err_clean, str(run.returncode)


def _normalize_map_entry(entry):
    """단일 명령 배열 또는 {a,b}/{commands} 이중 검증 항목을 (cmd_a, cmd_b, label_a, label_b)로 정규화."""
    if isinstance(entry, list) and entry and all(isinstance(x, str) for x in entry):
        return entry, None, shlex.join(entry), ''
    if not isinstance(entry, dict):
        return None, None, '', ''
    if 'a' in entry or 'b' in entry:
        a = entry.get('a')
        b = entry.get('b')
        return a, b, entry.get('label_a') or (shlex.join(a) if isinstance(a, list) else 'A'), entry.get('label_b') or (shlex.join(b) if isinstance(b, list) else 'B')
    commands = entry.get('commands')
    if isinstance(commands, list) and len(commands) >= 1:
        a = commands[0]
        b = commands[1] if len(commands) > 1 else None
        return a, b, 'A', 'B'
    return None, None, '', ''


def execute(entry, timeout, cwd):
    cmd_a, cmd_b, label_a, label_b = _normalize_map_entry(entry)
    if not isinstance(cmd_a, list) or not cmd_a or not all(isinstance(x, str) and x for x in cmd_a):
        return ('NOT_RUN', 'test-map 명령은 비어 있지 않은 문자열 배열이거나 {a,b} 이중 검증이어야 합니다',
                '', '', '', label_a, 'NOT_RUN', label_b, 'NOT_RUN')
    env = {**os.environ, 'QA_TEST_MODE': '1'}
    py_paths = [str(cwd / 'ai'), str(cwd)]
    if env.get('PYTHONPATH'):
        py_paths.append(env['PYTHONPATH'])
    env['PYTHONPATH'] = os.pathsep.join(py_paths)
    try:
        status_a, detail_a, out_a, err_a, code_a = _run_one(cmd_a, timeout, cwd, env)
    except FileNotFoundError as ex:
        return 'NOT_RUN', f'실행기 없음: {ex}', '', '', '', label_a, 'NOT_RUN', label_b, 'NOT_RUN'
    except subprocess.TimeoutExpired as ex:
        return 'FAIL', f'타임아웃 {timeout}초 초과', redact(ex.stdout), redact(ex.stderr), 'TIMEOUT', label_a, 'FAIL', label_b, 'NOT_RUN'
    except OSError as ex:
        return 'NOT_RUN', f'실행 환경 오류: {ex}', '', '', '', label_a, 'NOT_RUN', label_b, 'NOT_RUN'

    if cmd_b is None:
        # 이중 검증 없음 → 한쪽만 실행. PASS로 올리지 않고 RISK/NOT_RUN 취급 안내는 호출부에서.
        return (status_a, f'[단일검증] {detail_a}', out_a, err_a, code_a,
                label_a, status_a, label_b or '(미지정)', 'NOT_RUN')

    if not isinstance(cmd_b, list) or not cmd_b or not all(isinstance(x, str) and x for x in cmd_b):
        return (status_a if status_a != 'PASS' else 'NOT_RUN',
                f'검증 B 명령 형식 오류. A={status_a}', out_a, err_a, code_a,
                label_a, status_a, label_b, 'NOT_RUN')
    try:
        status_b, detail_b, out_b, err_b, code_b = _run_one(cmd_b, timeout, cwd, env)
    except (FileNotFoundError, OSError) as ex:
        return ('NOT_RUN', f'검증 B 실행 오류: {ex}. A={status_a}', out_a, err_a, code_a,
                label_a, status_a, label_b, 'NOT_RUN')
    except subprocess.TimeoutExpired as ex:
        return ('FAIL', f'검증 B 타임아웃. A={status_a}', out_a + '\n' + redact(ex.stdout or ''),
                err_a + '\n' + redact(ex.stderr or ''), 'TIMEOUT', label_a, status_a, label_b, 'FAIL')

    if status_a == 'PASS' and status_b == 'PASS':
        final = 'PASS'
    elif 'NOT_RUN' in (status_a, status_b):
        final = 'NOT_RUN'
    else:
        final = 'FAIL'
    detail = f'A[{status_a}] {detail_a} || B[{status_b}] {detail_b}'
    return (final, detail, out_a + '\n---\n' + out_b, err_a + '\n---\n' + err_b,
            f'{code_a}/{code_b}', label_a, status_a, label_b, status_b)


def atomic_tsv(path, headers, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.qa-updating-', suffix='.tmp', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.DictWriter(f, fieldnames=headers, delimiter='\t', lineterminator='\n', extrasaction='ignore')
            w.writeheader()
            w.writerows(rows)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _load_day_history(history_dir: Path | None, date: str, section_values: set[str]) -> list[dict]:
    if not history_dir:
        return []
    day_dir = history_dir / date
    if not day_dir.exists():
        return []
    items = []
    for jf in sorted(day_dir.glob('*.jsonl')):
        try:
            for line in jf.read_text(encoding='utf-8').splitlines():
                if not line.strip():
                    continue
                obj = json.loads(line)
                if obj.get('section') in section_values:
                    items.append(obj)
        except (OSError, json.JSONDecodeError):
            continue
    return items


def write_reports(group, folder, date, scope, history_dir=None):
    folder.mkdir(parents=True, exist_ok=True)
    total = Counter(c['status'] for c in group)
    now = datetime.now(TZ).isoformat(timespec='seconds')
    area = group[0]['area'] if group else ''
    section = group[0]['section'] if group else ''
    prefix = (f'영역: {area} | 섹션: {section} | 실행일: {now} | 실행범위: {scope} | 전체 {len(group)}건, '
              f"PASS {total['PASS']} / FAIL {total['FAIL']} / NOT_RUN {total['NOT_RUN']} / RISK {total['RISK']}\n\n")
    sec_names = {c['section'] for c in group}
    history_events = _load_day_history(history_dir, date, sec_names)

    for filename, name, states in [
        ('pass.md', 'PASS — 실제 실행 완료', {'PASS'}),
        ('fail.md', 'FAIL — 기대 결과 검증 실패', {'FAIL'}),
        ('risk.md', 'RISK / NOT_RUN — 미검증 및 추가 점검', {'RISK', 'NOT_RUN'}),
    ]:
        selected = [c for c in group if c['status'] in states]
        lines = [f'# {area} / {section} — {name}', '', prefix,
                 '| TC ID | 기능 | 유형 | 입력 | 예상결과 | 상태 | 검증A | 검증B | 실행일시 | 근거 |',
                 '|---|---|---|---|---|---|---|---|---|---|']
        for c in selected:
            lines.append('| ' + ' | '.join(mdesc(c.get(k)) for k in
                         ['tc_id', 'feature', 'kind', 'input', 'expected', 'status',
                          'tool_a_result', 'tool_b_result', 'stamp', 'detail']) + ' |')
        if not selected:
            lines.append('| — | — | — | — | — | 해당 없음 | — | — | — | — |')
        if filename == 'pass.md' and selected:
            for c in selected:
                lines += [
                    '', f"## {mdesc(c['tc_id'])} — {mdesc(c['feature'])}",
                    f"- 실행 시각: {mdesc(c['stamp'])}",
                    f"- 입력값: `{mdesc(c['input'])}`",
                    f"- 예상결과: {mdesc(c['expected'])}",
                    f"- 실제결과: {mdesc(c['detail'])}",
                    f"- 검증 A: `{mdesc(c.get('tool_a'))}` → {mdesc(c.get('tool_a_result'))}",
                    f"- 검증 B: `{mdesc(c.get('tool_b'))}` → {mdesc(c.get('tool_b_result'))}",
                    f"- 실행 명령: `{mdesc(c['command'])}` (종료 코드: `{mdesc(c['exit_code'])}`)",
                ]
                if (c.get('stdout') or '').strip():
                    lines += ['```text', c['stdout'].strip()[-600:], '```']
        if filename == 'fail.md':
            for c in selected:
                lines += [
                    '', f"## {mdesc(c['tc_id'])} — {mdesc(c['feature'])}",
                    f"- 실행 시각: {mdesc(c['stamp'])}",
                    f"- 입력값: `{mdesc(c['input'])}`",
                    f"- 예상결과: {mdesc(c['expected'])}",
                    f"- 실제결과: {mdesc(c['detail'])}",
                    f"- 검증 A: `{mdesc(c.get('tool_a'))}` → {mdesc(c.get('tool_a_result'))}",
                    f"- 검증 B: `{mdesc(c.get('tool_b'))}` → {mdesc(c.get('tool_b_result'))}",
                    f"- 실행 명령: `{mdesc(c['command'])}`",
                    f"- 종료 코드: {mdesc(c['exit_code'])}",
                    f"- 오류 재현 단계: 프로젝트 루트에서 `{mdesc(c['command'])}` 명령을 실행하여 동일 입력(`{mdesc(c['input'])}`)에 대한 assertion 실패를 재현합니다.",
                    '- 원인: 로그와 실제 코드를 조사해야 하며 자동으로 확정하지 않습니다. (제품 코드 수정 전 선보고 항목)',
                    '```text', (c['stderr'] or c['stdout'] or '(출력 없음)').strip(), '```',
                ]
        if filename == 'risk.md':
            lines += [
                '',
                '## 미실행(NOT_RUN) 및 잠재 위험(RISK) 분리 안내',
                '- NOT_RUN(미실행)은 PASS가 아니다. test-map 미연결·이중 검증 한쪽만 실행한 경우도 PASS로 올리지 않는다.',
                '- 부분 실행(`--tc` / `--section`)은 전체 배포 게이트 통과 근거가 아니다.',
                '- HIGH/CRITICAL RISK가 OPEN이면 병합·배포를 차단한다.',
                '- 결과 경로: `qa/results/<area>/<section>/<YYYY-MM-DD>/` (파일 5개, 영어명).',
            ]
        state_history = [ev for ev in history_events if ev.get('status') in states]
        if state_history:
            lines += ['', f'## 당일 누적 실행 이력 (`qa/history/{date}/`, 총 {len(state_history)}건)', '',
                      '| Run ID | 실행시각 | TC ID | 상태 | 종료코드 | 상세 |', '|---|---|---|---|---|---|']
            for ev in state_history[-30:]:
                lines.append('| ' + ' | '.join(mdesc(ev.get(k)) for k in ['run_id', 'stamp', 'tc_id', 'status', 'exit_code', 'detail']) + ' |')
        (folder / filename).write_text('\n'.join(lines) + '\n', encoding='utf-8')

    with (folder / 'results.tsv').open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(REPORT_COLUMNS)
        for c in group:
            w.writerow([
                c['tc_id'], c['area'], c['section'], c['feature'], c['kind'], c['input'], c['expected'],
                c['test_ref'], c['priority'], c['status'], c['detail'], c['command'], c['exit_code'], c['stamp'],
                c.get('tool_a', ''), c.get('tool_a_result', ''), c.get('tool_b', ''), c.get('tool_b_result', ''),
            ])


def main(argv=None):
    ap = argparse.ArgumentParser(description='TC 하나씩 실행하며 내부 TSV 시트와 4개 보고서를 실시간 갱신')
    ap.add_argument('--tsv', type=Path, default=ROOT/'qa/input/testcases.tsv')
    ap.add_argument('--map', dest='manifest', type=Path, default=ROOT/'qa/config/test_map.json')
    ap.add_argument('--output', type=Path, default=ROOT/'qa/results')
    ap.add_argument('--history', type=Path, default=ROOT/'qa/history')
    ap.add_argument('--date', default=None)
    ap.add_argument('--timeout', type=int, default=120)
    ap.add_argument('--tc', action='append', default=[], help='Run only specified TC ID; repeatable. NOT a full CI gate')
    ap.add_argument('--section', action='append', default=[], help='Run only specified section; repeatable')
    ap.add_argument('--no-update-sheet', action='store_true', help='Read-only source TSV; useful in CI')
    ap.add_argument('--no-excel', action='store_true', help='Skip exporting XLSX workbooks')
    ap.add_argument('--master-excel', type=Path, default=ROOT/'qa/master_test_sheet.xlsx',
                    help='Root aggregate is TSV (master_test_sheet.xlsx), not Excel')
    args = ap.parse_args(argv)
    if args.timeout <= 0:
        ap.error('timeout must be > 0')
    try:
        now = datetime.now(TZ)
        date = args.date or now.date().isoformat()
        if datetime.strptime(date, '%Y-%m-%d').date().isoformat() != date:
            raise ValueError('invalid date')
        cases, headers = load_cases(args.tsv)
        commands = json.loads(args.manifest.read_text(encoding='utf-8'))['cases']
        if not isinstance(commands, dict):
            raise ValueError('test-map cases must be an object')
        unknown_ids = set(args.tc) - {c['tc_id'] for c in cases}
        unknown_sections = set(args.section) - {c['section'] for c in cases}
        if unknown_ids or unknown_sections:
            raise ValueError(f'unknown TC/section: {sorted(unknown_ids)}, {sorted(unknown_sections)}')
    except (ValueError, FileNotFoundError, KeyError, json.JSONDecodeError) as ex:
        print(f'[QA CONFIG ERROR] {ex}', file=sys.stderr)
        return 2
    is_partial = bool(args.tc or args.section)
    selected = [c for c in cases if (not is_partial or c['tc_id'] in args.tc or c['section'] in args.section)]
    scope = 'PARTIAL (not a full gate)' if is_partial else 'FULL'
    run_id = f"{now.strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:8]}"
    events = args.history / date / f'{run_id}.jsonl'
    events.parent.mkdir(parents=True, exist_ok=True)
    augmented = list(dict.fromkeys(
        (['TC_ID', '영역', '섹션', '기능', '유형', '입력값', '예상결과', '테스트참조', '우선순위', '비고']
         + [h for h in headers if h not in STATUS_FIELDS]
         + STATUS_FIELDS)
    ))
    for c in cases:
        c.update(status='NOT_RUN', detail='아직 실행하지 않음' if c in selected else '이번 부분 실행 범위에 포함되지 않음',
                 stdout='', stderr='', command='', exit_code='', stamp='',
                 tool_a='', tool_a_result='NOT_RUN', tool_b='', tool_b_result='NOT_RUN')
    groups = defaultdict(list)
    for c in cases:
        groups[(c['area'], safe_section(c['section']))].append(c)
    touched_groups: set[tuple[str, str]] = set()

    def refresh(only_touched=False):
        if not args.no_update_sheet:
            rows = []
            for c in cases:
                row = dict(c['raw'])
                row.update({
                    '영역': c['area'], '섹션': c['section'], '기능': c['feature'], '유형': c['kind'],
                    '입력값': c['input'], '예상결과': c['expected'], '테스트참조': c['test_ref'],
                    '우선순위': c['priority'], '비고': c['memo'], 'TC_ID': c['tc_id'],
                    '상태': c['status'], '최근실행': c['stamp'], '상세': c['detail'],
                    '실행명령': c['command'], '종료코드': c['exit_code'],
                })
                rows.append(row)
            atomic_tsv(args.tsv, augmented, rows)
        for key, group in groups.items():
            # gate=qa/run.py 소유 TC는 test-map 미연결 NOT_RUN으로 이중검증 폴더를 덮지 않는다.
            if only_touched and key not in touched_groups:
                continue
            if all(('gate=qa/run.py' in (c.get('memo') or '')) and c['status'] == 'NOT_RUN' and not c.get('stamp') for c in group):
                continue
            if all(('gate=qa/run.py' in (c.get('memo') or '')) and c['status'] == 'NOT_RUN' and 'test-map 명령 연결 없음' in (c.get('detail') or '') for c in group):
                continue
            folder = result_dir(ROOT, group[0]['area'], group[0]['section'], date)
            if args.output != ROOT / 'qa' / 'results':
                folder = args.output / safe_section(group[0]['area']) / safe_section(group[0]['section']) / date
            write_reports(group, folder, date, scope, args.history)

    refresh(only_touched=True)
    total = Counter()
    with events.open('w', encoding='utf-8') as f:
        for index, c in enumerate(selected, 1):
            ref = c['test_ref'] or c['tc_id']
            cmd = commands.get(ref)
            gate_owned = 'gate=qa/run.py' in (c.get('memo') or '')
            if cmd is None:
                status, detail, stdout, stderr, exit_code = 'NOT_RUN', f'test-map 명령 연결 없음: {ref}', '', '', ''
                if gate_owned:
                    detail = f'게이트 소유 TC — python3 qa/run.py 로 이중 검증. ({detail})'
                tool_a, tool_a_result, tool_b, tool_b_result = '', 'NOT_RUN', '', 'NOT_RUN'
                command_text = ''
            else:
                (status, detail, stdout, stderr, exit_code,
                 tool_a, tool_a_result, tool_b, tool_b_result) = execute(cmd, args.timeout, ROOT)
                if isinstance(cmd, list):
                    command_text = shlex.join(cmd)
                    # 단일 검증만 있으면 PASS를 유지하지 않는다(이중 검증 정책).
                    if status == 'PASS':
                        status = 'NOT_RUN'
                        detail = f'이중 검증 미구성(단일 명령만). {detail}'
                        tool_b_result = 'NOT_RUN'
                elif isinstance(cmd, dict):
                    a, b, _, _ = _normalize_map_entry(cmd)
                    parts = []
                    if isinstance(a, list):
                        parts.append(shlex.join(a))
                    if isinstance(b, list):
                        parts.append(shlex.join(b))
                    command_text = ' || '.join(parts)
                else:
                    command_text = ''
            c.update(status=status, detail=detail, stdout=stdout, stderr=stderr, exit_code=exit_code,
                     stamp=datetime.now(TZ).isoformat(timespec='seconds'), command=command_text,
                     tool_a=tool_a, tool_a_result=tool_a_result, tool_b=tool_b, tool_b_result=tool_b_result)
            total[status] += 1
            key = (c['area'], safe_section(c['section']))
            # 게이트 소유 + map 없음이면 결과 폴더를 건드리지 않는다(시트/history만 갱신).
            if not (gate_owned and cmd is None):
                touched_groups.add(key)
            event = {k: c[k] for k in [
                'tc_id', 'area', 'section', 'feature', 'kind', 'input', 'expected', 'status', 'detail',
                'stamp', 'command', 'exit_code', 'stdout', 'stderr',
                'tool_a', 'tool_a_result', 'tool_b', 'tool_b_result']}
            event['run_id'] = run_id
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
            f.flush()
            refresh(only_touched=True)
            print(f'[{index}/{len(selected)}] {c["tc_id"]} ({c["area"]}/{c["section"]}) = {status}', flush=True)
    if not args.no_excel:
        excel = subprocess.run([sys.executable, str(ROOT / 'scripts/export_qa_excel.py'),
                                '--tsv', str(args.tsv), '--output', str(args.output),
                                '--master', str(args.master_excel), '--date', date],
                               cwd=ROOT, check=False)
        if excel.returncode:
            print('NOTICE: XLSX export not available; QA execution evidence and TSV remain intact.', file=sys.stderr)
    print('DONE:', dict(total), 'scope=', scope, 'events=', events)
    if is_partial or total['FAIL'] or total['NOT_RUN'] or total['RISK']:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
