"""로컬 파일 기반 보안 데이터 룩업 (CISA KEV, MITRE CWE, OWASP 매핑)"""
import json

from src.core.config import MODELS_DIR

_kev = None
_cwe = None


def load_lookups():
    """처음 한 번만 파일을 읽고 메모리에 캐싱한다."""
    global _kev, _cwe
    if _kev is None:
        _kev = set(json.loads((MODELS_DIR / "kev_cves.json").read_text(encoding="utf-8")))
        _cwe = json.loads((MODELS_DIR / "cwe_info.json").read_text(encoding="utf-8"))
    return _kev, _cwe


def is_in_kev(cve_id: str) -> bool:
    """해당 CVE가 CISA KEV(실제 악용이 확인된 취약점)에 포함되어 있는지 확인한다."""
    kev, _ = load_lookups()
    return cve_id in kev


def cwe_info(cwe_id: int | str):
    """CWE 번호 → {"name": ..., "owasp": "A05", "owasp_name": "인젝션"}"""
    _, cwe = load_lookups()
    return cwe.get(str(cwe_id), {"name": "Unknown", "owasp": "OTHER", "owasp_name": "Top 10 외"})
