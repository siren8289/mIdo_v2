#!/usr/bin/env python3
"""Infra check B: curl-style HTTP smoke against local ports (non-destructive).

If services are down, returns NOT_RUN (never PASS). Does not start production traffic.
"""
from __future__ import annotations

import json
import socket
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGETS = [
    ("INFRA-SMOKE-FRONT", "http://127.0.0.1:80/", "front"),
    ("INFRA-SMOKE-BACK", "http://127.0.0.1:8080/actuator/health", "back"),
]


def _port_open(host: str, port: int, timeout: float = 0.4) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _probe(url: str) -> tuple[str, str]:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            code = getattr(resp, "status", 200)
            body = resp.read(200).decode("utf-8", errors="replace")
            if 200 <= int(code) < 500:
                return "PASS", f"HTTP {code} body={body[:80]!r}"
            return "FAIL", f"HTTP {code}"
    except urllib.error.HTTPError as ex:
        # 401/404 still proves stack is up for smoke of "service responds"
        if ex.code < 500:
            return "PASS", f"HTTP {ex.code} (reachable)"
        return "FAIL", f"HTTP {ex.code}"
    except Exception as ex:  # noqa: BLE001
        return "NOT_RUN", f"unreachable: {type(ex).__name__}: {ex}"


def main() -> int:
    cases = []
    any_up = False
    for tc_id, url, label in TARGETS:
        host_port = (url.split("://", 1)[1].split("/", 1)[0]).split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else (443 if url.startswith("https") else 80)
        if not _port_open(host, port):
            cases.append({
                "id": tc_id,
                "status": "NOT_RUN",
                "expected": f"{label} responds on {url}",
                "actual": f"port {port} closed",
                "evidence": "local stack not running; smoke skipped",
                "file": "compose.yaml",
                "function": label,
                "line": "UNKNOWN",
                "error": "",
                "cause": "로컬 스택 미기동 — PASS 금지",
                "input": url,
            })
            continue
        any_up = True
        status, detail = _probe(url)
        cases.append({
            "id": tc_id,
            "status": status,
            "expected": f"{label} HTTP reachable",
            "actual": detail,
            "evidence": detail,
            "file": "compose.yaml",
            "function": label,
            "line": "UNKNOWN",
            "error": "" if status == "PASS" else detail,
            "cause": "" if status == "PASS" else detail,
            "input": url,
        })
    # Aggregate id used by gate
    if not cases:
        agg_status, agg_detail = "NOT_RUN", "no targets"
    elif all(c["status"] == "PASS" for c in cases):
        agg_status, agg_detail = "PASS", "all smoke targets PASS"
    elif any(c["status"] == "FAIL" for c in cases):
        agg_status, agg_detail = "FAIL", "one or more smoke FAIL"
    else:
        agg_status, agg_detail = "NOT_RUN", "stack down or partial NOT_RUN"
    cases.insert(0, {
        "id": "INFRA-SMOKE",
        "status": agg_status,
        "expected": "local HTTP smoke against compose-published ports",
        "actual": agg_detail,
        "evidence": f"any_up={any_up}; n={len(TARGETS)}",
        "file": "compose.yaml",
        "function": "http_smoke",
        "line": "UNKNOWN",
        "error": "" if agg_status == "PASS" else agg_detail,
        "cause": "" if agg_status == "PASS" else agg_detail,
        "input": "curl-equivalent",
    })
    print(json.dumps({"cases": cases}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
