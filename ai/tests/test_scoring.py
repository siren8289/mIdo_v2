"""CVSS 점수 계산 및 피처 엔지니어링 단위 테스트"""
from src.scoring import (
    CATEGORY_COLUMNS,
    FEATURE_COLUMNS,
    NUMBER_COLUMNS,
    cvss3_base_score,
    make_ml_frame,
    parse_cvss_vector,
    round_up,
    severity_from_score,
)


def test_cvss_calculation():
    # Log4Shell (CVE-2021-44228) CVSS v3.1 vector
    vector = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H"
    assert cvss3_base_score(vector) == 10.0
    assert severity_from_score(10.0) == "CRITICAL"


def test_cvss_severity_thresholds():
    assert severity_from_score(9.5) == "CRITICAL"
    assert severity_from_score(9.0) == "CRITICAL"
    assert severity_from_score(8.9) == "HIGH"
    assert severity_from_score(7.0) == "HIGH"
    assert severity_from_score(6.9) == "MEDIUM"
    assert severity_from_score(4.0) == "MEDIUM"
    assert severity_from_score(3.9) == "LOW"


def test_round_up():
    assert round_up(4.01) == 4.1
    assert round_up(4.0) == 4.0
    assert round_up(0.0) == 0.0


def test_make_ml_frame():
    rows = [
        {
            "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
            "cvss_score": 7.5,
            "owasp": "A05",
        }
    ]
    df = make_ml_frame(rows)
    assert len(df) == 1
    assert list(df.columns) == FEATURE_COLUMNS
    assert df.iloc[0]["attack_vector"] == "N"
    assert df.iloc[0]["cvss_score"] == 7.5
    assert df.iloc[0]["owasp"] == "A05"
