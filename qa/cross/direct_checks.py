#!/usr/bin/env python3
"""pytest 없이 같은 함수를 호출하는 두 번째 단위 도구이자 보안 동작 도구."""
import importlib.util
import inspect
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AI = ROOT / "ai"
sys.path.insert(0, str(AI))
sys.path.insert(0, str(ROOT))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _loc(obj) -> tuple[str, str, str]:
    try:
        lines, start = inspect.getsourcelines(obj)
        file = Path(inspect.getsourcefile(obj) or "")
        try:
            file = file.resolve().relative_to(ROOT)
        except ValueError:
            file = file
        return str(file), getattr(obj, "__name__", "UNKNOWN"), str(start)
    except (OSError, TypeError):
        return "UNKNOWN", "UNKNOWN", "UNKNOWN"


def _case(tc_id, status, expected, actual, evidence, obj, input_value="", error="", cause=""):
    file, function, line = _loc(obj) if obj is not None else ("UNKNOWN", "UNKNOWN", "UNKNOWN")
    return {
        "id": tc_id,
        "status": status,
        "expected": expected,
        "actual": actual,
        "evidence": evidence,
        "file": file,
        "function": function,
        "line": line,
        "input": input_value,
        "error": error,
        "cause": cause,
    }


def _unit(cases: list) -> None:
    from datetime import date

    import pandas as pd
    from src.parser.dependency import parse_dependencies
    from src.scoring.cvss import cvss3_base_score, parse_cvss_vector
    from data.etl.transform import build_dataset, clean_nvd, cwe_to_number, owasp_code, severity_from_score

    text = '{"dependencies":{"lodash":"^4.17.15"},"devDependencies":{"vite":"5.0.0"}}'
    file_type, deps = parse_dependencies(text)
    names = {item["name"]: item["version"] for item in deps}
    ok = file_type == "package.json" and names.get("lodash") == "4.17.15" and names.get("vite") == "5.0.0"
    cases.append(_case(
        "UNIT-PKG", "PASS" if ok else "FAIL",
        "package.json, lodash 4.17.15, vite 5.0.0",
        f"{file_type} {names}",
        "parse_dependencies 직접 호출",
        parse_dependencies, text,
        cause="" if ok else "파서 결과가 기존 test_package_json 기대와 다르다.",
    ))

    req = "requests==2.19.0\n# 주석\nflask>=2.0\n"
    file_type, deps = parse_dependencies(req)
    ok = file_type == "requirements.txt" and deps == [{"ecosystem": "pypi", "name": "requests", "version": "2.19.0"}]
    cases.append(_case(
        "UNIT-REQ", "PASS" if ok else "FAIL",
        "requirements.txt, requests==2.19.0만",
        f"{file_type} {deps}",
        "주석과 >= 줄은 제외",
        parse_dependencies, req,
        cause="" if ok else "requirements 파서 결과가 기대와 다르다.",
    ))

    vector = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H"
    parsed = parse_cvss_vector(vector)
    score = cvss3_base_score(vector)
    ok = parsed.get("attack_vector") == "N" and score == 10.0
    cases.append(_case(
        "UNIT-CVSS-10", "PASS" if ok else "FAIL",
        "attack_vector N, base 10.0",
        f"AV={parsed.get('attack_vector')} score={score}",
        "Log4Shell 벡터 직접 계산",
        cvss3_base_score, vector,
        cause="" if ok else "CVSS 10.0 기대와 다르다.",
    ))

    cwe = cwe_to_number("CWE-79")
    none = cwe_to_number("NVD-CWE-noinfo")
    a05 = owasp_code(79)
    other = owasp_code(9999)
    ok = cwe == 79 and none is None and a05 == "A05" and other == "OTHER"
    cases.append(_case(
        "UNIT-CWE", "PASS" if ok else "FAIL",
        "79, None, A05, OTHER",
        f"{cwe}, {none}, {a05}, {other}",
        "cwe_to_number, owasp_code 직접 호출",
        cwe_to_number,
        cause="" if ok else "CWE/OWASP 매핑이 기대와 다르다.",
    ))

    bands = [severity_from_score(n) for n in (9.8, 7.5, 5.0, 1.2)]
    ok = bands == ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    cases.append(_case(
        "UNIT-SEV", "PASS" if ok else "FAIL",
        "CRITICAL HIGH MEDIUM LOW",
        " ".join(bands),
        "severity_from_score 경계 근처 값",
        severity_from_score,
        cause="" if ok else "심각도 구간이 기대와 다르다.",
    ))

    cves = [
        {"id": "CVE-2025-0001", "vulnStatus": "Rejected", "published": "2025-01-01T00:00:00.000",
         "descriptions": [{"lang": "en", "value": "rejected"}], "metrics": {}, "weaknesses": [], "references": []},
        {"id": "CVE-2025-0002", "vulnStatus": "Analyzed", "published": "2025-01-02T00:00:00.000",
         "descriptions": [{"lang": "en", "value": "Cross site scripting in example package allows attackers to run script."}],
         "metrics": {"cvssMetricV31": [{"type": "Primary", "cvssData": {"baseScore": 6.1, "vectorString": "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N", "baseSeverity": "MEDIUM"}}]},
         "weaknesses": [{"description": [{"value": "CWE-79"}]}], "references": [{"url": "https://example.com"}]},
    ]
    frame = clean_nvd(cves)
    ids = list(frame["cve_id"])
    cwe_id = int(frame.iloc[0]["cwe_id"]) if len(frame) else None
    ok = ids == ["CVE-2025-0002"] and cwe_id == 79
    cases.append(_case(
        "UNIT-NVD", "PASS" if ok else "FAIL",
        "Rejected 제거, CVE-2025-0002, CWE 79",
        f"{ids} cwe={cwe_id}",
        "clean_nvd 가짜 CVE 2건",
        clean_nvd,
        cause="" if ok else "Rejected CVE 필터가 기대와 다르다.",
    ))

    nvd = pd.DataFrame([{
        "cve_id": "CVE-2025-9999", "published": date(2025, 1, 1), "description": "demo",
        "cvss_score": 9.8, "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "severity": "CRITICAL", "cwe_id": 78, "reference_count": 1,
    }])
    epss = pd.DataFrame([{"cve_id": "CVE-2025-9999", "epss": 0.8, "epss_percentile": 0.99}])
    kev = pd.DataFrame([{"cve_id": "CVE-2025-9999", "kev_ransomware": False}])
    cwe_frame = pd.DataFrame([{"cwe_id": 78, "cwe_name": "OS Command Injection", "owasp": "A05"}])
    built = build_dataset(nvd, epss, kev, cwe_frame, date(2025, 2, 1))
    row = built.iloc[0]
    ok = int(row["exploit_label"]) == 1 and int(row["in_kev"]) == 1 and row["owasp"] == "A05"
    cases.append(_case(
        "UNIT-LABEL", "PASS" if ok else "FAIL",
        "exploit_label 1, in_kev 1, owasp A05",
        f"label={int(row['exploit_label'])} kev={int(row['in_kev'])} owasp={row['owasp']}",
        "build_dataset 가짜 표",
        build_dataset,
        cause="" if ok else "학습 라벨이 기대와 다르다.",
    ))

    processed = ROOT / "data" / "processed"
    missing = [name for name in ("owasp_stats.csv", "cwe_clean.csv", "kev_clean.csv") if not (processed / name).exists()]
    cases.append(_case(
        "UNIT-FILES", "PASS" if not missing else "FAIL",
        "owasp_stats.csv, cwe_clean.csv, kev_clean.csv 존재",
        "있음" if not missing else f"없음: {missing}",
        "data/processed 파일 존재 확인",
        None,
        cause="" if not missing else "전처리 산출물이 없다.",
    ))
    cases[-1]["file"] = "data/processed"
    cases[-1]["function"] = "UNKNOWN"
    cases[-1]["line"] = "UNKNOWN"


def _security(cases: list) -> None:
    from src.parser.dependency import parse_dependencies, parse_package_json
    from src.scoring.cvss import cvss3_base_score
    from src.features.vulnerability_rag_001.harness.runtime import validate_tool_permission

    allowed, reason = validate_tool_permission("shell_exec")
    cases.append(_case(
        "SEC-TOOL-UNKNOWN",
        "FAIL" if allowed else "PASS",
        "등록되지 않은 도구는 거부(False)",
        f"allowed={allowed} reason={reason}",
        "validate_tool_permission('shell_exec')",
        validate_tool_permission,
        "shell_exec",
        "" if not allowed else "거부 사유 없이 허용",
        "금지 목록에 없을 때 return True 라서 미등록 도구가 허용된다.",
    ))

    denied, deny_reason = validate_tool_permission("file_edit")
    cases.append(_case(
        "SEC-TOOL-DENY",
        "PASS" if denied is False else "FAIL",
        "file_edit 거부",
        f"allowed={denied} reason={deny_reason}",
        "validate_tool_permission('file_edit')",
        validate_tool_permission,
        "file_edit",
        cause="" if denied is False else "file_edit이 거부되지 않았다.",
    ))

    invalid = [
        "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:X/C:H/I:H/A:H",
        "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:/C:H/I:H/A:H",
    ]
    scores = {item: cvss3_base_score(item) for item in invalid}
    bad = {item: score for item, score in scores.items() if score is not None}
    cases.append(_case(
        "SEC-CVSS-SX",
        "FAIL" if bad else "PASS",
        "잘못된 S 값은 점수 None",
        str(scores),
        "cvss3_base_score 직접 호출",
        cvss3_base_score,
        " | ".join(invalid),
        "" if not bad else "점수가 반환됨",
        "S가 U/C가 아니어도 KeyError가 나지 않으면 점수를 계산한다.",
    ))

    payload = {"dependencies": {f"pkg{i}": "1.0.0" for i in range(51)}}
    file_type, deps = parse_dependencies(json.dumps(payload))
    silent = len(deps) == 50
    cases.append(_case(
        "SEC-CAP",
        "FAIL" if silent else "PASS",
        "51개면 51개를 반환하거나 잘림을 결과에 알림",
        f"type={file_type} count={len(deps)} return=tuple",
        "parse_dependencies 51개",
        parse_dependencies,
        "package.json dependencies 51개",
        "" if not silent else "반환 51개가 아님. 경고 필드 없음",
        "MAX_DEPENDENCIES 슬라이스만 하고 호출자에게 잘림을 알리지 않는다.",
    ))

    dup = '{"dependencies":{"lodash":"1.0.0"},"devDependencies":{"lodash":"1.0.0"}}'
    parsed = parse_package_json(dup)
    cases.append(_case(
        "SEC-DUP",
        "FAIL" if len(parsed) != 1 else "PASS",
        "같은 이름·버전은 1건",
        f"count={len(parsed)} {parsed}",
        "parse_package_json dependencies+devDependencies",
        parse_package_json,
        dup,
        cause="섹션을 이어 붙일 때 중복을 제거하지 않는다." if len(parsed) != 1 else "",
    ))

    owasp = _load("mido_owasp_direct", AI / "src" / "service" / "owasp.py")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp)
        (path / "owasp_stats.json").write_text(json.dumps([{"cve_count": -1}]), encoding="utf-8")
        owasp.MODELS_DIR = path
        try:
            report = owasp.owasp_report()
            total = report.get("total_cves")
            neg = isinstance(total, (int, float)) and total < 0
            cases.append(_case(
                "SEC-OWASP-NEG",
                "FAIL" if neg else "PASS",
                "cve_count 음수는 합계를 0 미만으로 만들지 않음",
                f"total_cves={total}",
                "임시 owasp_stats.json cve_count=-1",
                owasp.owasp_report,
                "[{\"cve_count\": -1}]",
                cause="음수 cve_count를 그대로 더한다." if neg else "",
            ))
        except Exception as exc:  # noqa: BLE001 — 도구 결과로 남긴다
            cases.append(_case(
                "SEC-OWASP-NEG", "ERROR", "합계가 0 이상인 dict",
                type(exc).__name__, str(exc), owasp.owasp_report, "[{\"cve_count\": -1}]", str(exc),
            ))

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp)
        (path / "owasp_stats.json").write_text("{", encoding="utf-8")
        owasp.MODELS_DIR = path
        try:
            report = owasp.owasp_report()
            controlled = isinstance(report, dict)
            cases.append(_case(
                "SEC-OWASP-CORRUPT",
                "PASS" if controlled else "FAIL",
                "깨진 JSON은 예외를 올리지 않고 오류 dict",
                str(report),
                "임시 owasp_stats.json '{'",
                owasp.owasp_report,
                "{",
            ))
        except json.JSONDecodeError as exc:
            cases.append(_case(
                "SEC-OWASP-CORRUPT", "FAIL",
                "JSONDecodeError 대신 오류 dict",
                f"JSONDecodeError: {exc}",
                "임시 파일 '{'",
                owasp.owasp_report, "{", str(exc),
                "json.loads 예외를 잡지 않는다.",
            ))
        except Exception as exc:  # noqa: BLE001
            cases.append(_case(
                "SEC-OWASP-CORRUPT", "ERROR", "오류 dict",
                type(exc).__name__, str(exc), owasp.owasp_report, "{", str(exc),
            ))

    lookups = _load("mido_lookups_direct", AI / "src" / "evidence" / "lookups.py")
    with tempfile.TemporaryDirectory() as tmp:
        lookups._kev = None
        lookups._cwe = None
        lookups.MODELS_DIR = Path(tmp)
        try:
            value = lookups.load_lookups()
            cases.append(_case(
                "SEC-KEV-MISSING", "PASS",
                "KEV 파일이 없으면 통제된 응답",
                f"returned {type(value).__name__}",
                "빈 디렉터리로 load_lookups",
                lookups.load_lookups,
            ))
        except FileNotFoundError as exc:
            cases.append(_case(
                "SEC-KEV-MISSING", "FAIL",
                "FileNotFoundError가 아닌 준비 상태 응답",
                f"FileNotFoundError: {exc.filename}",
                "없는 kev_cves.json",
                lookups.load_lookups, str(exc.filename), str(exc),
                "파일 부재를 잡지 않고 FileNotFoundError가 전파된다.",
            ))
        except Exception as exc:  # noqa: BLE001
            cases.append(_case(
                "SEC-KEV-MISSING", "FAIL",
                "통제된 응답",
                f"{type(exc).__name__}: {exc}",
                "없는 kev_cves.json",
                lookups.load_lookups, "", str(exc),
                "준비 실패가 호출자 예외로 전파된다.",
            ))


def main() -> None:
    cases: list = []
    try:
        _unit(cases)
        _security(cases)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"tool": "direct_checks", "error": f"{type(exc).__name__}: {exc}", "cases": cases}, ensure_ascii=False))
        return
    print(json.dumps({"tool": "direct_checks", "cases": cases}, ensure_ascii=False))


if __name__ == "__main__":
    main()
