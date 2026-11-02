#!/usr/bin/env python3
"""Verify Hook/watcher/CI wiring exists and basic commands run (V3 requirement)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKS = []


def ok(name: str, detail: str = "") -> None:
    CHECKS.append(("PASS", name, detail))
    print(f"PASS {name} {detail}")


def bad(name: str, detail: str) -> None:
    CHECKS.append(("FAIL", name, detail))
    print(f"FAIL {name} {detail}", file=sys.stderr)


def main() -> int:
    required = [
        ROOT / "qa-policy.md",
        ROOT / "AGENTS.md",
        ROOT / ".agents/skills/tsv-qa/SKILL.md",
        ROOT / "qa/config/test_map.json",
        ROOT / "qa/hooks/stop_gate.py",
        ROOT / "scripts/watch_qa.py",
        ROOT / "scripts/run_qa.py",
        ROOT / "qa/run.py",
        ROOT / ".github/workflows/ci.yml",
    ]
    for path in required:
        if path.exists():
            ok("exists", str(path.relative_to(ROOT)))
        else:
            bad("missing", str(path.relative_to(ROOT)))

    ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    if "qa-gate" in ci and "python3 qa/run.py" in ci and ("pull_request" in ci):
        ok("ci_qa_gate", "push/PR qa-gate wired")
    else:
        bad("ci_qa_gate", "qa-gate or triggers missing")

    # stop_gate dry run (empty stdin)
    proc = subprocess.run(
        [sys.executable, str(ROOT / "qa/hooks/stop_gate.py")],
        cwd=ROOT, input="{}", text=True, capture_output=True, check=False,
    )
    if proc.returncode == 0:
        ok("stop_gate", (proc.stdout or proc.stderr or "ok")[:120])
    else:
        bad("stop_gate", proc.stderr or str(proc.returncode))

    # watcher syntax only (full --once would execute entire TSV; too heavy for wiring check)
    watch = subprocess.run(
        [sys.executable, "-m", "py_compile", str(ROOT / "scripts/watch_qa.py")],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    if watch.returncode == 0:
        ok("watch_qa_syntax", "py_compile ok")
    else:
        bad("watch_qa_syntax", watch.stderr[-300:] or str(watch.returncode))

    tsv = ROOT / "qa/input/testcases.tsv"
    if tsv.exists() and tsv.stat().st_size > 0:
        ok("testcases_tsv", f"bytes={tsv.stat().st_size}")
    else:
        bad("testcases_tsv", "missing or empty")

    # cross tools smoke import
    for script in [
        "qa/cross/compose_checks.py",
        "qa/cross/dockerfile_checks.py",
        "qa/cross/http_smoke.py",
    ]:
        r = subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, capture_output=True, text=True, check=False)
        try:
            data = json.loads(r.stdout or "{}")
            if "cases" in data:
                ok(script, f"cases={len(data['cases'])}")
            else:
                bad(script, "no cases json")
        except json.JSONDecodeError:
            bad(script, (r.stderr or r.stdout)[-200:])

    fails = [c for c in CHECKS if c[0] == "FAIL"]
    print(f"DONE pass={len(CHECKS)-len(fails)} fail={len(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
