"""2단계: 전처리. 받아 온 원본을 학습에 쓸 수 있는 깔끔한 표로 바꾼다.

전처리 순서
  1. NVD JSON 펼치기 (중첩된 JSON → 한 줄에 CVE 1건인 표)
  2. 잘못된 데이터 제거 (거절된 CVE, 영어 설명 없음, CVSS 점수 없음, 중복)
  3. 글자 정리 (설명의 줄바꿈·연속 공백 정리, CWE 번호를 숫자로)
  4. 4개 데이터 합치기 (NVD + EPSS + KEV + CWE)
  5. 결측치 채우기 (EPSS 없음 → 0, CWE 없음 → 0 = '알 수 없음')
  6. 파생 변수 (OWASP 분류, 공개 후 지난 일수, 참고 링크 수)
  7. 정답(라벨) 만들기: KEV 에 있거나 EPSS ≥ 10% 이면 1(악용 위험 높음)
"""
import json
import re

import pandas as pd

from data.etl.config import EPSS_HIGH_THRESHOLD, OWASP_TOP10_2025

# CWE 번호 → OWASP 코드 빠른 조회표.  예) 79 → "A05"
CWE_TO_OWASP = {}
for code, info in OWASP_TOP10_2025.items():
    for cwe in info["cwes"]:
        CWE_TO_OWASP.setdefault(cwe, code)


# ---------- 작은 도우미 함수 ----------

def clean_text(text):
    """줄바꿈·탭·연속 공백을 공백 1칸으로 바꾼다."""
    if not isinstance(text, str):
        return ""
    return re.sub(r"\s+", " ", text).strip()


def cwe_to_number(value):
    """'CWE-79' → 79.  'NVD-CWE-noinfo' 처럼 번호가 없으면 None."""
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"CWE-(\d+)", value.strip())
    return int(match.group(1)) if match else None


def owasp_code(cwe_id):
    """CWE 번호 → OWASP 코드. 모르는 CWE는 'OTHER'."""
    if pd.isna(cwe_id):
        return "OTHER"
    return CWE_TO_OWASP.get(int(cwe_id), "OTHER")


def severity_from_score(score):
    """CVSS 점수 → 등급 (CVSS v3 공식 기준)"""
    if score >= 9.0:
        return "CRITICAL"
    if score >= 7.0:
        return "HIGH"
    if score >= 4.0:
        return "MEDIUM"
    return "LOW"


# ---------- 1~3. NVD ----------

def pick_cvss(metrics):
    """CVSS v3.1 → 없으면 v3.0 순서로 고른다. NVD 가 매긴 'Primary' 점수를 먼저 쓴다."""
    for key in ["cvssMetricV31", "cvssMetricV30"]:
        items = metrics.get(key) or []
        items = sorted(items, key=lambda item: item.get("type") != "Primary")  # Primary 를 앞으로
        if items:
            data = items[0]["cvssData"]
            return data.get("baseScore"), data.get("vectorString"), data.get("baseSeverity")
    return None, None, None


def pick_cwe(weaknesses):
    """여러 CWE 중 번호가 있는 첫 번째 것을 고른다."""
    for weakness in weaknesses or []:
        for item in weakness.get("description", []):
            number = cwe_to_number(item.get("value"))
            if number is not None:
                return number
    return None


def clean_nvd(cves):
    """NVD 원본 리스트 → CVE 표"""
    rows = []
    for cve in cves:
        # 거절(Rejected)된 CVE 는 취약점이 아니므로 뺀다.
        if cve.get("vulnStatus") == "Rejected":
            continue

        english = [d["value"] for d in cve.get("descriptions", []) if d.get("lang") == "en"]
        score, vector, severity = pick_cvss(cve.get("metrics", {}))

        rows.append({
            "cve_id": cve.get("id"),
            "published": cve.get("published"),
            "description": clean_text(english[0]) if english else "",
            "cvss_score": score,
            "cvss_vector": vector,
            "severity": severity,
            "cwe_id": pick_cwe(cve.get("weaknesses")),
            "reference_count": len(cve.get("references", [])),
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    # CVSS 점수나 설명이 없으면 학습할 수 없으므로 뺀다. 점수 0점(영향 없음)도 뺀다.
    df = df.dropna(subset=["cvss_score", "cvss_vector"])
    df = df[df["cvss_score"] > 0]
    df = df[df["description"].str.len() > 20]
    # 같은 CVE 가 두 번 들어온 경우 (기간이 겹칠 때) 하나만 남긴다.
    df = df.drop_duplicates(subset="cve_id")

    df["published"] = pd.to_datetime(df["published"]).dt.date
    # 등급이 비어 있으면 점수로 계산해서 채운다.
    df["severity"] = df["severity"].fillna(df["cvss_score"].apply(severity_from_score))
    return df.reset_index(drop=True)


# ---------- EPSS / KEV / CWE ----------

def clean_epss(path):
    """EPSS CSV → cve_id, epss, epss_percentile.  첫 줄은 '#model_version...' 설명이라 건너뛴다."""
    df = pd.read_csv(path, skiprows=1)
    df = df.rename(columns={"cve": "cve_id", "percentile": "epss_percentile"})
    return df[["cve_id", "epss", "epss_percentile"]].drop_duplicates(subset="cve_id")


def clean_kev(path):
    """KEV JSON → cve_id, kev_date_added, kev_ransomware"""
    body = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for item in body.get("vulnerabilities", []):
        rows.append({
            "cve_id": item["cveID"],
            "kev_name": item.get("vulnerabilityName", ""),
            "kev_date_added": item.get("dateAdded"),
            # 랜섬웨어 공격에 쓰였는지: "Known" / "Unknown"
            "kev_ransomware": item.get("knownRansomwareCampaignUse") == "Known",
        })
    return pd.DataFrame(rows).drop_duplicates(subset="cve_id")


def clean_cwe(path):
    """CWE CSV(zip) → cwe_id, cwe_name.  이 CSV는 줄 끝에 쉼표가 하나 더 있어서 index_col=False 가 필요하다."""
    df = pd.read_csv(path, index_col=False)
    df = df.rename(columns={"CWE-ID": "cwe_id", "Name": "cwe_name"})
    df["cwe_id"] = pd.to_numeric(df["cwe_id"], errors="coerce")
    df = df.dropna(subset=["cwe_id"])
    df["cwe_id"] = df["cwe_id"].astype(int)
    df["owasp"] = df["cwe_id"].apply(owasp_code)
    return df[["cwe_id", "cwe_name", "owasp"]]


# ---------- 4~7. 합치기 + 라벨 ----------

def build_dataset(nvd, epss, kev, cwe, today):
    """NVD 를 기준으로 나머지 3개를 붙이고, 파생 변수와 정답(라벨)을 만든다."""
    df = nvd.merge(epss, on="cve_id", how="left")
    df = df.merge(kev[["cve_id", "kev_ransomware"]], on="cve_id", how="left", indicator="kev_join")
    df["in_kev"] = (df["kev_join"] == "both").astype(int)
    df = df.drop(columns=["kev_join", "kev_ransomware"])

    # 결측치: EPSS 점수가 아직 없는 CVE 는 '악용 신호 없음'으로 보고 0으로 채운다.
    df["epss"] = df["epss"].fillna(0.0)
    df["epss_percentile"] = df["epss_percentile"].fillna(0.0)
    # 결측치: CWE 가 없는 CVE 는 0번(알 수 없음)으로 둔다.
    df["cwe_id"] = df["cwe_id"].fillna(0).astype(int)
    df = df.merge(cwe[["cwe_id", "cwe_name"]], on="cwe_id", how="left")
    df["cwe_name"] = df["cwe_name"].fillna("Unknown")

    # 파생 변수
    df["owasp"] = df["cwe_id"].apply(owasp_code)
    df["age_days"] = (pd.Timestamp(today) - pd.to_datetime(df["published"])).dt.days.clip(lower=0)

    # 정답(라벨): 1 = 악용 위험 높음
    df["exploit_label"] = ((df["in_kev"] == 1) | (df["epss"] >= EPSS_HIGH_THRESHOLD)).astype(int)
    return df


def make_owasp_stats(dataset):
    """OWASP 분류별 요약: CVE 수, 평균 CVSS, 평균 EPSS, KEV 비율, 악용 위험 비율"""
    stats = dataset.groupby("owasp").agg(
        cve_count=("cve_id", "count"),
        avg_cvss=("cvss_score", "mean"),
        avg_epss=("epss", "mean"),
        kev_rate=("in_kev", "mean"),
        exploit_rate=("exploit_label", "mean"),
    ).round(4).reset_index()
    names = {code: info["name"] for code, info in OWASP_TOP10_2025.items()}
    stats.insert(1, "owasp_name", stats["owasp"].map(names).fillna("Top 10 외"))
    return stats.sort_values("owasp")
