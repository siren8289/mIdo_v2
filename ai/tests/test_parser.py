"""의존성 파서와 CVSS 점수 계산이 맞는지 확인한다."""
from src.dependency_parser import parse_dependencies
from src.features import cvss3_base_score, parse_cvss_vector


def test_package_json():
    text = '{"dependencies":{"lodash":"^4.17.15"},"devDependencies":{"vite":"5.0.0"}}'
    file_type, deps = parse_dependencies(text)
    assert file_type == "package.json"
    names = {item["name"]: item["version"] for item in deps}
    assert names["lodash"] == "4.17.15"
    assert names["vite"] == "5.0.0"


def test_requirements():
    text = "requests==2.19.0\n# 주석\nflask>=2.0\n"
    file_type, deps = parse_dependencies(text)
    assert file_type == "requirements.txt"
    assert deps == [{"ecosystem": "pypi", "name": "requests", "version": "2.19.0"}]


def test_cvss_log4shell():
    # Log4Shell 대표 벡터. 점수는 10.0 이어야 한다.
    vector = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H"
    assert parse_cvss_vector(vector)["attack_vector"] == "N"
    assert cvss3_base_score(vector) == 10.0
