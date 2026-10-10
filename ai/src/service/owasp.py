"""기능 2: OWASP Top 10 공공데이터 현황 리포트"""
import json

from src.core.config import MODELS_DIR


def owasp_report():
    """공공데이터로 생성된 OWASP Top 10 통계 데이터를 조회하여 반환한다."""
    path = MODELS_DIR / "owasp_stats.json"
    if not path.exists():
        return {"items": [], "total_cves": 0}
    items = json.loads(path.read_text(encoding="utf-8"))
    return {"items": items, "total_cves": sum(item.get("cve_count", 0) for item in items)}
