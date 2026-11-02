#!/usr/bin/env python3
"""Opt-in local QC watcher. While alive, run the full manifest after source changes.

No daemon/background promise; stop with Ctrl+C. Only tests in a trusted manifest run.
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUFFIX = {'.py', '.java', '.kt', '.js', '.jsx', '.ts', '.tsx', '.go', '.json', '.yaml', '.yml', '.html', '.css', '.sh', '.sql'}
IGNORED = {'.git', '.venv', 'venv', 'node_modules', 'dist', 'build', 'coverage', '.next', '.idea', '__pycache__', '.pytest_cache'}

def snapshot():
    result = {}
    for file in ROOT.rglob('*'):
        if not file.is_file() or file.suffix not in SUFFIX:
            continue
        rel = file.relative_to(ROOT)
        if set(rel.parts) & IGNORED or rel.parts[0] in {'qa', '.agents', '.claude', '.grok', 'docs'}:
            continue
        try:
            s = file.stat()
            result[str(rel)] = (s.st_mtime_ns, s.st_size)
        except OSError:
            continue
    # These two files also trigger a run when AI adds a TC or binds a test.
    for special in ('qa/input/testcases.tsv', 'qa/config/test_map.json'):
        path = ROOT / special
        if path.exists():
            stat = path.stat()
            result[special] = (stat.st_mtime_ns, stat.st_size)
    return result

def main():
    ap = argparse.ArgumentParser(description='Local QC watcher; blocks until Ctrl+C')
    ap.add_argument('--interval', type=float, default=2.0, help='Poll interval seconds')
    ap.add_argument('--debounce', type=float, default=2.0, help='Quiet time before re-running')
    ap.add_argument('--once', action='store_true', help='Run QA once and exit (sanity check)')
    args = ap.parse_args()
    if args.interval <= 0 or args.debounce <= 0:
        ap.error('interval/debounce must be positive')
    command = [sys.executable, str(ROOT/'scripts/run_qa.py')]
    if args.once:
        return subprocess.run(command, cwd=ROOT, check=False).returncode
    seen = snapshot()
    pending = None
    print(f'QC watcher ON: {ROOT}. Ctrl+C to stop. Only repo-local trusted test-map commands can run.', flush=True)
    try:
        while True:
            time.sleep(args.interval)
            latest = snapshot()
            if latest != seen:
                changed = sorted(set(latest) ^ set(seen) | {x for x in latest.keys() & seen.keys() if latest[x] != seen[x]})
                print('Source changed:', ', '.join(changed[:10]) or '(multiple)', flush=True)
                seen = latest
                pending = time.monotonic()
            if pending is not None and time.monotonic() - pending >= args.debounce:
                print('Running QA on all mapped TCs...', flush=True)
                code = subprocess.run(command, cwd=ROOT, check=False).returncode
                print(f'QC finished: exit={code}. New source edits trigger another run.', flush=True)
                seen = snapshot()
                pending = None
    except KeyboardInterrupt:
        print('\nQC watcher stopped by user.', flush=True)
        return 0

if __name__ == '__main__':
    sys.exit(main())
