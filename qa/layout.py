"""QA V3 layout: English areas, snake_case paths, append-only result logs."""
from __future__ import annotations

import re
from pathlib import Path

AREAS: dict[str, str] = {
    "01_unit_integration": "01_unit_integration",
    "02_web_api": "02_web_api",
    "03_security_quality": "03_security_quality",
    "04_infra_deploy": "04_infra_deploy",
}
AREA_ALIASES: dict[str, str] = {
    "단위·통합 테스트": "01_unit_integration",
    "unit": "01_unit_integration",
    "integration": "01_unit_integration",
    "웹·API 테스트": "02_web_api",
    "api": "02_web_api",
    "e2e": "02_web_api",
    "web": "02_web_api",
    "보안·품질 검사": "03_security_quality",
    "security": "03_security_quality",
    "quality": "03_security_quality",
    "인프라·배포 검사": "04_infra_deploy",
    "regression": "04_infra_deploy",
    "infra": "04_infra_deploy",
    "deploy": "04_infra_deploy",
}
AREA_LABELS = tuple(AREAS.keys())
AREA_FOLDERS = tuple(AREAS.values())
TYPE_TO_AREA = {
    "unit": "01_unit_integration",
    "integration": "01_unit_integration",
    "api": "02_web_api",
    "e2e": "02_web_api",
    "web": "02_web_api",
    "security": "03_security_quality",
    "quality": "03_security_quality",
    "regression": "04_infra_deploy",
    "infra": "04_infra_deploy",
    "deploy": "04_infra_deploy",
}

DAY_FILES = ("test_sheet.xlsx", "pass.md", "fail.md", "risk.md", "results.tsv")
MASTER_XLSX = "master_test_sheet.xlsx"
EXECUTION_LOG = "execution_log.tsv"
TEST_MAP = "test_map.json"


def safe_name(value: str, fallback: str = "uncategorized") -> str:
    text = (value or "").strip().lower()
    text = text.replace("·", "_").replace(" ", "_").replace("-", "_").replace(".", "_")
    text = re.sub(r"[^0-9a-z_]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    if not text or re.search(r"[가-힣]", value or ""):
        ascii_only = re.sub(r"[^0-9a-z_]+", "_", text).strip("_")
        text = ascii_only or fallback
    return text[:80] or fallback


def normalize_area(value: str) -> str:
    text = (value or "").strip()
    if text in AREAS:
        return text
    if text in AREA_ALIASES:
        return AREA_ALIASES[text]
    mapped = TYPE_TO_AREA.get(text.lower())
    if mapped:
        return mapped
    raise ValueError(f"Unknown QA area: {value!r}. Allowed: {', '.join(AREA_LABELS)}")


def area_folder(area_label: str) -> str:
    return AREAS[normalize_area(area_label)]


def result_dir(root: Path, area: str, section: str, date: str) -> Path:
    return root / "qa" / "results" / area_folder(area) / safe_name(section) / date


def master_path(root: Path) -> Path:
    return root / "qa" / MASTER_XLSX


def execution_log_path(root: Path) -> Path:
    return root / "qa" / "history" / EXECUTION_LOG


def test_map_path(root: Path) -> Path:
    return root / "qa" / "config" / TEST_MAP


def ensure_area_tree(root: Path) -> list[Path]:
    created: list[Path] = []
    base = root / "qa" / "results"
    for folder in AREA_FOLDERS:
        path = base / folder
        path.mkdir(parents=True, exist_ok=True)
        keep = path / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")
        created.append(path)
    (root / "qa" / "history").mkdir(parents=True, exist_ok=True)
    return created
