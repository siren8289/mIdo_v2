#!/usr/bin/env python3
"""Infra check B for compose: Dockerfiles exist for front/back/ai."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = [
    "front/Dockerfile",
    "back/Dockerfile",
    "ai/Dockerfile",
]


def main() -> int:
    missing = [rel for rel in FILES if not (ROOT / rel).is_file()]
    ok = not missing
    cases = [{
        "id": "INFRA-COMPOSE",
        "status": "PASS" if ok else "FAIL",
        "expected": "front/back/ai Dockerfiles present",
        "actual": "ok" if ok else f"missing={missing}",
        "evidence": f"checked={FILES} missing={missing}",
        "file": missing[0] if missing else FILES[0],
        "function": "Dockerfile",
        "line": "UNKNOWN",
        "error": "" if ok else f"missing {missing}",
        "cause": "" if ok else "이미지 빌드 정의 누락",
        "input": "Dockerfiles",
    }]
    print(json.dumps({"cases": cases}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
