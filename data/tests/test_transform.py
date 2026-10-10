"""전처리 함수가 기대대로 동작하는지 확인한다. (인터넷 없이 작은 가짜 데이터로)"""
from datetime import date
from pathlib import Path

from data.etl.transform import build_dataset, clean_nvd, cwe_to_number, owasp_code, severity_from_score


def test_cwe_and_owasp():
    assert cwe_to_number("CWE-79") == 79
    assert cwe_to_number("NVD-CWE-noinfo") is None
    assert owasp_code(79) == "A05"  # XSS → 인젝션
    assert owasp_code(9999) == "OTHER"


def test_severity():
    assert severity_from_score(9.8) == "CRITICAL"
    assert severity_from_score(7.5) == "HIGH"
    assert severity_from_score(5.0) == "MEDIUM"
    assert severity_from_score(1.2) == "LOW"


def test_clean_nvd_drops_rejected():
    cves = [
        {
            "id": "CVE-2025-0001",
            "vulnStatus": "Rejected",
            "published": "2025-01-01T00:00:00.000",
            "descriptions": [{"lang": "en", "value": "rejected"}],
            "metrics": {},
            "weaknesses": [],
            "references": [],
        },
        {
            "id": "CVE-2025-0002",
            "vulnStatus": "Analyzed",
            "published": "2025-01-02T00:00:00.000",
            "descriptions": [{"lang": "en", "value": "Cross site scripting in example package allows attackers to run script."}],
            "metrics": {
                "cvssMetricV31": [{
                    "type": "Primary",
                    "cvssData": {
                        "baseScore": 6.1,
                        "vectorString": "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N",
                        "baseSeverity": "MEDIUM",
                    },
                }]
            },
            "weaknesses": [{"description": [{"value": "CWE-79"}]}],
            "references": [{"url": "https://example.com"}],
        },
    ]
    df = clean_nvd(cves)
    assert list(df["cve_id"]) == ["CVE-2025-0002"]
    assert int(df.iloc[0]["cwe_id"]) == 79


def test_build_dataset_label():
    import pandas as pd

    nvd = pd.DataFrame([{
        "cve_id": "CVE-2025-9999",
        "published": date(2025, 1, 1),
        "description": "demo",
        "cvss_score": 9.8,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "severity": "CRITICAL",
        "cwe_id": 78,
        "reference_count": 1,
    }])
    epss = pd.DataFrame([{"cve_id": "CVE-2025-9999", "epss": 0.8, "epss_percentile": 0.99}])
    kev = pd.DataFrame([{"cve_id": "CVE-2025-9999", "kev_ransomware": False}])
    cwe = pd.DataFrame([{"cwe_id": 78, "cwe_name": "OS Command Injection", "owasp": "A05"}])

    df = build_dataset(nvd, epss, kev, cwe, date(2025, 2, 1))
    assert int(df.iloc[0]["exploit_label"]) == 1
    assert int(df.iloc[0]["in_kev"]) == 1
    assert df.iloc[0]["owasp"] == "A05"


def test_processed_files_exist():
    processed = Path(__file__).resolve().parents[1] / "processed"
    # 큰 학습표(cve_dataset.csv)는 git에 올리지 않는다.
    assert (processed / "owasp_stats.csv").exists()
    assert (processed / "cwe_clean.csv").exists()
    assert (processed / "kev_clean.csv").exists()
