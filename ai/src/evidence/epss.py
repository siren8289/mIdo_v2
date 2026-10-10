"""FIRST EPSS (Exploit Prediction Scoring System) API 실시간 조회"""
import httpx

from src.core.config import EPSS_URL, TIMEOUT_SECONDS


def fetch_epss(cve_ids: list[str]) -> dict[str, float]:
    """CVE 여러 개의 30일 내 실제 악용 확률(EPSS)을 한 번에 조회한다. 실패 시 빈 딕셔너리 반환."""
    if not cve_ids:
        return {}
    try:
        response = httpx.get(
            EPSS_URL,
            params={"cve": ",".join(sorted(cve_ids)[:100])},
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return {row["cve"]: float(row["epss"]) for row in response.json().get("data", [])}
    except (httpx.HTTPError, ValueError, KeyError):
        return {}
