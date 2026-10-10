"""보안 데이터 수집 및 룩업 단위 테스트"""
from src.evidence import cwe_info, find_fixed_version, is_in_kev


def test_kev_lookup():
    # Log4Shell is in KEV
    assert is_in_kev("CVE-2021-44228") is True
    # Non-existent CVE
    assert is_in_kev("CVE-9999-99999") is False


def test_cwe_lookup():
    # CWE-89 (SQL Injection) -> A05
    info = cwe_info(89)
    assert info["owasp"] == "A05"

    # Unknown CWE
    unknown = cwe_info(0)
    assert unknown["name"] == "Unknown"
    assert unknown["owasp"] == "OTHER"


def test_find_fixed_version():
    vuln = {
        "affected": [
            {
                "package": {"name": "lodash"},
                "ranges": [
                    {"events": [{"introduced": "0"}, {"fixed": "4.17.21"}]}
                ],
            }
        ]
    }
    assert find_fixed_version(vuln, "lodash") == "4.17.21"
    assert find_fixed_version(vuln, "express") is None
