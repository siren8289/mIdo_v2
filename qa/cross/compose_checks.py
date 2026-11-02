#!/usr/bin/env python3
"""Infra check A: Docker Compose services and healthcheck definitions (static)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    compose = ROOT / "compose.yaml"
    cases = []
    if not compose.exists():
        cases.append({
            "id": "INFRA-COMPOSE",
            "status": "FAIL",
            "expected": "compose.yaml exists with services and healthchecks",
            "actual": "compose.yaml missing",
            "evidence": "file missing",
            "file": "compose.yaml",
            "function": "services",
            "line": "UNKNOWN",
            "error": "compose.yaml not found",
            "cause": "배포 정의 파일 부재",
            "input": "compose.yaml",
        })
        print(json.dumps({"cases": cases}, ensure_ascii=False))
        return 1

    text = compose.read_text(encoding="utf-8")
    required = ["services:", "healthcheck:", "front:", "back:", "ai:"]
    missing = [item for item in required if item not in text]
    ok = not missing
    cases.append({
        "id": "INFRA-COMPOSE",
        "status": "PASS" if ok else "FAIL",
        "expected": "compose.yaml defines front/back/ai and healthcheck",
        "actual": "ok" if ok else f"missing={missing}",
        "evidence": f"compose.yaml bytes={compose.stat().st_size} missing={missing}",
        "file": "compose.yaml",
        "function": "healthcheck",
        "line": "UNKNOWN",
        "error": "" if ok else f"missing keys: {missing}",
        "cause": "" if ok else "필수 서비스/헬스체크 정의 누락",
        "input": "compose.yaml",
    })
    print(json.dumps({"cases": cases}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
