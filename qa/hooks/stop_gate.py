#!/usr/bin/env python3
"""제품 소스가 마지막 QA 스탬프보다 새로우면 Stop을 막는다.

전체 스위트는 돌리지 않는다. 이미 기록된 HIGH를 이유로 반복 차단하지 않는다.
병합 차단은 qa/run.py 종료 코드와 CI qa-gate가 담당한다.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = ROOT / "qa" / "results" / ".last_run"
SKIP_DIRS = {
    "__pycache__",
    "node_modules",
    "build",
    "dist",
    ".gradle",
    ".pytest_cache",
}
WATCH_FILES = [
    "compose.yaml",
    "front/nginx.conf",
    "front/Dockerfile",
    "back/Dockerfile",
    "ai/Dockerfile",
    "scripts/deploy.sh",
    "qa/run.py",
    "qa/recorder.py",
]
WATCH_DIRS = [
    "front/src",
    "back/src",
    "ai/src",
    "data/etl",
    "data/tests",
    ".github/workflows",
    "qa/cross",
    "qa/hooks",
]


def latest_mtime() -> float:
    latest = 0.0
    for rel in WATCH_FILES:
        path = ROOT / rel
        if path.is_file():
            latest = max(latest, path.stat().st_mtime)
    for rel in WATCH_DIRS:
        path = ROOT / rel
        if not path.exists():
            continue
        for file in path.rglob("*"):
            if not file.is_file() or any(part in SKIP_DIRS for part in file.parts):
                continue
            latest = max(latest, file.stat().st_mtime)
    return latest


def main() -> None:
    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {}
    reason = str(payload.get("reason") or payload.get("stop_reason") or "")
    if reason in {"channel_closed", "shutdown"}:
        return
    if not STAMP.exists():
        print(json.dumps({
            "decision": "block",
            "reason": "QA 게이트 기록이 없습니다. 저장소 루트에서 python3 qa/run.py 를 실행한 뒤 마무리하세요.",
        }, ensure_ascii=False))
        return
    if latest_mtime() > STAMP.stat().st_mtime + 0.05:
        print(json.dumps({
            "decision": "block",
            "reason": "제품 소스 또는 QA 게이트가 qa/results/.last_run 보다 새롭습니다. python3 qa/run.py 로 교차 검증과 날짜별 기록을 갱신한 뒤 마무리하세요.",
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
