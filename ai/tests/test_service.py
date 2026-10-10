"""서비스 로직 및 리포트 생성 단위 테스트"""
from src.service.analyzer import _empty_report, _level, _priority
from src.service.owasp import owasp_report


def test_empty_report():
    report = _empty_report("package.json", "라이브러리를 찾지 못했습니다.")
    assert report["file_type"] == "package.json"
    assert report["dependencies"] == []
    assert report["findings"] == []
    assert report["summary"]["dependency_count"] == 0
    assert report["explanation"] == "라이브러리를 찾지 못했습니다."


def test_priority_calculation():
    item_in_kev = {
        "in_kev": True,
        "epss": 0.5,
        "severity": "CRITICAL",
        "ml_exploit_risk": 0.8,
    }
    # 100 + 0.5*40 + 4*8 + 0.8*20 = 100 + 20 + 32 + 16 = 168.0
    priority = _priority(item_in_kev)
    assert priority == 168.0

    item_low = {
        "in_kev": False,
        "epss": 0.01,
        "severity": "LOW",
        "ml_exploit_risk": 0.1,
    }
    # 0 + 0.01*40 + 1*8 + 0.1*20 = 0.4 + 8 + 2 = 10.4
    assert round(_priority(item_low), 1) == 10.4


def test_level_determination():
    assert _level([], kev_count=1) == "critical"
    assert _level([{"severity": "CRITICAL"}], kev_count=0) == "critical"
    assert _level([{"severity": "HIGH", "epss": 0.05, "ml_exploit_risk": 0.2}], kev_count=0) == "high"
    assert _level([{"severity": "MEDIUM", "epss": 0.01, "ml_exploit_risk": 0.1}], kev_count=0) == "medium"
    assert _level([], kev_count=0) == "none"


def test_owasp_report():
    report = owasp_report()
    assert "items" in report
    assert "total_cves" in report
    assert report["total_cves"] >= 0
