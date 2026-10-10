"""CVSS v3.1 벡터 파싱 및 기본 점수(Base Score) 계산 공식

CVSS 벡터 예) CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
  AV 공격 경로 (N 네트워크 / A 인접 / L 로컬 / P 물리)
  AC 공격 난이도 (L 쉬움 / H 어려움)
  PR 필요한 권한 (N 없음 / L 낮음 / H 높음)
  UI 사용자 상호작용 필요 여부 (N 필요 없음 / R 필요)
  S  영향 범위 (U 변경 없음 / C 다른 시스템까지 전파)
  C·I·A 기밀성·무결성·가용성 영향도 (H 큼 / L 작음 / N 없음)

계산식 공식 출처: https://www.first.org/cvss/v3.1/specification-document (7.1절)
"""
import math

# 벡터 약자 → 필드 매핑
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

# CVSS v3.1 공식 계산 가중치
WEIGHTS = {
    "AV": {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2},
    "AC": {"L": 0.77, "H": 0.44},
    "UI": {"N": 0.85, "R": 0.62},
    "CIA": {"H": 0.56, "L": 0.22, "N": 0.0},
}


def parse_cvss_vector(vector: str | None) -> dict[str, str]:
    """'CVSS:3.1/AV:N/...' → {'attack_vector': 'N', ...}. 파싱할 수 없는 값은 'X'."""
    values = {column: "X" for column in CVSS_PARTS.values()}
    if not isinstance(vector, str) or not vector.startswith("CVSS:3"):
        return values
    for part in vector.split("/")[1:]:
        if ":" in part:
            key, value = part.split(":", 1)
            if key in CVSS_PARTS:
                values[CVSS_PARTS[key]] = value
    return values


def round_up(value: float) -> float:
    """CVSS 공식 올림: 소수 첫째 자리까지 올린다. 예) 4.02 → 4.1"""
    integer = round(value * 100000)
    if integer % 10000 == 0:
        return integer / 100000.0
    return (math.floor(integer / 10000) + 1) / 10.0


def cvss3_base_score(vector: str | None) -> float | None:
    """CVSS v3.1 벡터 → 0.0~10.0 점수 계산. 파싱 불가 시 None 반환."""
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


def severity_from_score(score: float) -> str:
    """CVSS 점수 → 심각도 등급 (CVSS v3 공식 기준)"""
    if score >= 9.0:
        return "CRITICAL"
    if score >= 7.0:
        return "HIGH"
    if score >= 4.0:
        return "MEDIUM"
    return "LOW"
