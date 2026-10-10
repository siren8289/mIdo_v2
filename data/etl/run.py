"""데이터 파이프라인 실행: 수집 → 전처리 → 저장

사용법 (저장소 루트에서)
    python -m data.etl.run --days 365

만들어지는 파일 (data/processed/)
    cve_dataset.csv   학습용 CVE 표 (NVD + EPSS + KEV + CWE + OWASP, 라벨 포함)
    kev_clean.csv     KEV 전체 목록 (AI 서버가 'KEV 에 있나?' 확인할 때 사용)
    cwe_clean.csv     CWE 번호 → 이름 → OWASP 분류
    owasp_stats.csv   OWASP 분류별 요약 통계
"""
import argparse
from datetime import date, timedelta

from data.etl.fetch import fetch_cwe, fetch_epss, fetch_kev, fetch_nvd, fetch_nvd_kev
from data.etl.load import save_processed, save_raw_json
from data.etl.transform import (
    build_dataset,
    clean_cwe,
    clean_epss,
    clean_kev,
    clean_nvd,
    make_owasp_stats,
)


def run(days):
    today = date.today()
    start = today - timedelta(days=days)
    print(f"NVD 수집 기간: {start} ~ {today}")

    # 1) 수집 + 원본 저장
    print("[1/3] 수집")
    nvd_raw = fetch_nvd(start, today) + fetch_nvd_kev()
    save_raw_json(nvd_raw, "nvd_cves")
    epss_path = fetch_epss()
    kev_path = fetch_kev()
    cwe_path = fetch_cwe()

    # 2) 전처리
    print("[2/3] 전처리")
    nvd = clean_nvd(nvd_raw)
    print(f"  NVD: 원본 {len(nvd_raw)}건 → 정제 {len(nvd)}건 (거절·점수 없음·중복 제거)")
    epss = clean_epss(epss_path)
    kev = clean_kev(kev_path)
    cwe = clean_cwe(cwe_path)
    print(f"  EPSS {len(epss)}건 / KEV {len(kev)}건 / CWE {len(cwe)}건")

    dataset = build_dataset(nvd, epss, kev, cwe, today)
    positive = int(dataset["exploit_label"].sum())
    print(f"  학습 데이터 {len(dataset)}건, 악용 위험 높음(라벨 1) {positive}건")

    # 3) 저장
    print("[3/3] 저장")
    print("  ", save_processed(dataset, "cve_dataset"))
    print("  ", save_processed(kev, "kev_clean"))
    print("  ", save_processed(cwe, "cwe_clean"))
    print("  ", save_processed(make_owasp_stats(dataset), "owasp_stats"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NVD·EPSS·KEV·CWE 수집 + 전처리")
    parser.add_argument("--days", type=int, default=365, help="최근 며칠 동안 공개된 CVE를 모을지 (기본 365)")
    args = parser.parse_args()
    run(args.days)
