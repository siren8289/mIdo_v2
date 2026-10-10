"""1단계: 공공 보안 데이터를 인터넷에서 받아 온다.

- NVD   : REST API (JSON). 한 번에 2,000건 · 120일까지만 줘서 여러 번 나눠 부른다.
- EPSS  : 매일 올라오는 CSV 파일(gzip 압축) 1개
- KEV   : JSON 파일 1개
- CWE   : CSV 파일(zip 압축) 1개
"""
import time
from datetime import timedelta

import requests

from data.etl.config import (
    CWE_URL,
    EPSS_URL,
    KEV_URL,
    NVD_API_KEY,
    NVD_MAX_DAYS,
    NVD_PAGE_SIZE,
    NVD_SLEEP_SECONDS,
    NVD_URL,
    RAW_DIR,
)


def get_with_retry(url, params=None, headers=None, tries=3):
    """요청이 실패하면(서버 바쁨 등) 조금 쉬었다가 최대 3번까지 다시 시도한다."""
    for attempt in range(1, tries + 1):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=60)
            response.raise_for_status()
            return response
        except requests.RequestException as error:
            print(f"    요청 실패 ({attempt}/{tries}): {error}")
            if attempt == tries:
                raise
            time.sleep(10 * attempt)


def date_windows(start, end):
    """[start, end] 기간을 NVD 규칙(최대 120일)에 맞게 잘게 나눈다."""
    windows = []
    current = start
    while current < end:
        window_end = min(current + timedelta(days=NVD_MAX_DAYS), end)
        windows.append((current, window_end))
        current = window_end
    return windows


def fetch_nvd_pages(url, params, label):
    """NVD 는 한 번에 2,000건만 주므로, startIndex 를 늘려 가며 끝까지 받는다."""
    headers = {"apiKey": NVD_API_KEY} if NVD_API_KEY else {}
    cves = []
    start_index = 0
    while True:
        page_params = {**params, "resultsPerPage": NVD_PAGE_SIZE, "startIndex": start_index}
        body = get_with_retry(url, params=page_params, headers=headers).json()

        # 응답 모양: {"totalResults": 123, "vulnerabilities": [{"cve": {...}}, ...]}
        items = [item["cve"] for item in body.get("vulnerabilities", [])]
        cves.extend(items)
        total = body.get("totalResults", 0)
        print(f"  NVD {label}: {start_index + len(items)}/{total}건")

        time.sleep(NVD_SLEEP_SECONDS)  # 요청 제한을 지키기 위해 쉰다
        start_index += NVD_PAGE_SIZE
        if start_index >= total:
            return cves


def fetch_nvd(start, end):
    """기간 안에 '공개(published)'된 CVE를 모두 받는다."""
    all_cves = []
    for window_start, window_end in date_windows(start, end):
        params = {
            "pubStartDate": window_start.strftime("%Y-%m-%dT00:00:00.000"),
            "pubEndDate": window_end.strftime("%Y-%m-%dT00:00:00.000"),
        }
        label = f"{window_start:%Y-%m-%d}~{window_end:%Y-%m-%d}"
        all_cves.extend(fetch_nvd_pages(NVD_URL, params, label))
    return all_cves


def fetch_nvd_kev():
    """KEV(실제 악용 확인)에 오른 CVE 를 NVD 에서 모두 받는다. (hasKev 옵션)

    최근 1년 CVE 만 모으면 '악용됨(정답 1)' 예시가 너무 적어서(약 0.5%)
    예전 CVE 라도 실제로 악용된 것들을 학습 데이터에 더한다.
    """
    return fetch_nvd_pages(f"{NVD_URL}?hasKev", {}, "KEV")


def download_file(url, file_name):
    """파일을 data/raw/ 에 그대로 저장하고 경로를 돌려준다. (EPSS, KEV, CWE 공통)"""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / file_name
    response = get_with_retry(url)
    path.write_bytes(response.content)
    print(f"  다운로드: {file_name} ({len(response.content) // 1024:,} KB)")
    return path


def fetch_epss():
    return download_file(EPSS_URL, "epss_scores.csv.gz")


def fetch_kev():
    return download_file(KEV_URL, "kev.json")


def fetch_cwe():
    return download_file(CWE_URL, "cwe_1000.csv.zip")
