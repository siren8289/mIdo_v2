"""학습과 예측이 '똑같은 방식'으로 입력을 만들도록 공통 함수를 모아 둔다.

CVSS 벡터 예)  CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
  AV 공격 경로 (N 네트워크 / A 인접 / L 로컬 / P 물리)
  AC 공격 난이도 (L 쉬움 / H 어려움)
  PR 필요한 권한 (N 없음 / L 낮음 / H 높음)
  UI 사용자 클릭 등 필요 여부 (N 필요 없음 / R 필요)
  S  영향 범위 (U 그대로 / C 다른 시스템까지)
  C·I·A 기밀성·무결성·가용성 피해 (H 큼 / L 작음 / N 없음)
"""
import math

import pandas as pd

# 벡터의 약자 → 표 컬럼 이름
CVSS_PARTS = {
    "AV": "attack_vector",
    "AC": "attack_complexity",
    "PR": "privileges",
    "UI": "user_interaction",
    "S": "scope",
    "C": "confidentiality",
    "I": "integrity",
    "A": "availability",
}

# ---------- ML(악용 위험 예측) 입력 ----------
CATEGORY_COLUMNS = list(CVSS_PARTS.values()) + ["owasp"]
NUMBER_COLUMNS = ["cvss_score"]
FEATURE_COLUMNS = CATEGORY_COLUMNS + NUMBER_COLUMNS
TARGET_COLUMN = "exploit_label"   # 1 = KEV 에 있거나 EPSS ≥ 10%

# ---------- DL(설명 글 → 심각도) 입력 ----------
TEXT_COLUMN = "description"
SEVERITY_LABELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

# CVSS 점수가 없을 때 등급으로 대신 쓸 대표 점수
SEVERITY_TO_SCORE = {"LOW": 2.5, "MEDIUM": 5.5, "HIGH": 8.0, "CRITICAL": 9.5}


def parse_cvss_vector(vector):
    """'CVSS:3.1/AV:N/...' → {'attack_vector': 'N', ...}.  모르는 값은 'X'."""
    values = {column: "X" for column in CVSS_PARTS.values()}
    if not isinstance(vector, str) or not vector.startswith("CVSS:3"):
        return values
    for part in vector.split("/")[1:]:
        if ":" in part:
            key, value = part.split(":", 1)
            if key in CVSS_PARTS:
                values[CVSS_PARTS[key]] = value
    return values


def make_ml_frame(rows):
    """[{cvss_vector, cvss_score, owasp}, ...] → ML 모델에 넣을 표"""
    records = []
    for row in rows:
        record = parse_cvss_vector(row.get("cvss_vector"))
        record["owasp"] = row.get("owasp") or "OTHER"
        record["cvss_score"] = float(row.get("cvss_score") or 0.0)
        records.append(record)
    return pd.DataFrame(records, columns=FEATURE_COLUMNS)


def severity_from_score(score):
    """CVSS 점수 → 등급 (CVSS v3 공식 기준)"""
    if score >= 9.0:
        return "CRITICAL"
    if score >= 7.0:
        return "HIGH"
    if score >= 4.0:
        return "MEDIUM"
    return "LOW"


# ---------- CVSS v3.1 기본 점수 계산 ----------
# OSV 는 점수 숫자 없이 벡터 글자만 줄 때가 많아서, 공식 계산식으로 직접 점수를 구한다.
# 계산식 출처: https://www.first.org/cvss/v3.1/specification-document (7.1절)

WEIGHTS = {
    "AV": {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2},
    "AC": {"L": 0.77, "H": 0.44},
    "UI": {"N": 0.85, "R": 0.62},
    "CIA": {"H": 0.56, "L": 0.22, "N": 0.0},
}


def round_up(value):
    """CVSS 공식 올림: 소수 첫째 자리까지 올린다. 예) 4.02 → 4.1"""
    integer = round(value * 100000)
    if integer % 10000 == 0:
        return integer / 100000.0
    return (math.floor(integer / 10000) + 1) / 10.0


def cvss3_base_score(vector):
    """CVSS v3 벡터 → 0.0~10.0 점수.  읽을 수 없으면 None."""
    parts = parse_cvss_vector(vector)
    try:
        av = WEIGHTS["AV"][parts["attack_vector"]]
        ac = WEIGHTS["AC"][parts["attack_complexity"]]
        ui = WEIGHTS["UI"][parts["user_interaction"]]
        c = WEIGHTS["CIA"][parts["confidentiality"]]
        i = WEIGHTS["CIA"][parts["integrity"]]
        a = WEIGHTS["CIA"][parts["availability"]]
        changed = parts["scope"] == "C"
        # 권한(PR)은 영향 범위가 바뀌면(S:C) 가중치가 달라진다.
        pr = {"N": 0.85, "L": 0.68 if changed else 0.62, "H": 0.5 if changed else 0.27}[parts["privileges"]]
    except KeyError:
        return None

    iss = 1 - (1 - c) * (1 - i) * (1 - a)
    if changed:
        impact = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02) ** 15
    else:
        impact = 6.42 * iss
    exploitability = 8.22 * av * ac * pr * ui

    if impact <= 0:
        return 0.0
    if changed:
        return round_up(min(1.08 * (impact + exploitability), 10))
    return round_up(min(impact + exploitability, 10))
