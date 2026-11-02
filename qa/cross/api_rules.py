#!/usr/bin/env python3
"""ScanRequest의 @NotBlank와 @Size(min=3, max=80000)만 검사한다. HTTP는 열지 않는다."""
import json


def rejection(value) -> str | None:
    """거절 이유. None이면 통과."""
    if value is None:
        return "null"
    if not isinstance(value, str):
        return "type"
    if value.strip() == "":
        return "blank"
    if len(value) < 3 or len(value) > 80000:
        return "size"
    return None


def _request_line() -> str:
    from pathlib import Path

    file = Path(__file__).resolve().parents[2] / "back/src/main/java/com/mido/scan/dto/ScanRequest.java"
    if not file.exists():
        return "UNKNOWN"
    for index, line in enumerate(file.read_text(encoding="utf-8").splitlines(), start=1):
        if "@NotBlank" in line:
            return str(index)
    return "UNKNOWN"


def _case(tc_id, value, expect_reject: bool):
    reason = rejection(value)
    rejected = reason is not None
    ok = rejected is expect_reject
    shown = "null" if value is None else (f"len={len(value)}" if isinstance(value, str) and len(value) > 40 else repr(value))
    return {
        "id": tc_id,
        "status": "PASS" if ok else "FAIL",
        "expected": "거절" if expect_reject else "허용",
        "actual": f"거절:{reason}" if rejected else "허용",
        "evidence": "Bean Validation 규칙의 파이썬 재구현. 소켓과 MockMvc는 사용하지 않음",
        "file": "back/src/main/java/com/mido/scan/dto/ScanRequest.java",
        "function": "ScanRequest",
        "line": _request_line(),
        "input": shown,
        "error": "" if ok else "규칙 재구현 결과가 기대와 다름",
        "cause": "" if ok else "NotBlank/Size 판정이 기대와 다름",
    }


def main() -> None:
    cases = [
        _case("API-EMPTY", "", True),
        _case("API-NULL", None, True),
        _case("API-BLANK", "   ", True),
        _case("API-SHORT", "ab", True),
        _case("API-MIN", "abc", False),
        _case("API-MAX", "a" * 80000, False),
        _case("API-OVER", "a" * 80001, True),
    ]
    print(json.dumps({"tool": "api_rules", "cases": cases}, ensure_ascii=False))


if __name__ == "__main__":
    main()
