---
name: tsv-qa
description: Use on every code change and before every commit/push for MIDO QA·Security V3 dual-verify TSV cases.
---
# TSV QA Skill V3 (single skill)

## Always (including every commit/push)
1. Follow `qa-policy.md` + `AGENTS.md`.
2. Source TC: `qa/input/testcases.tsv` (imported from `qa/input/atomic_testcases_872.xlsx`).
3. Run `python3 qa/run.py` before claiming done / before push. CI also runs `qa-gate` on every push/PR.
4. FAIL/RISK: record under `qa/results/...` and `qa/history/execution_log.tsv` **before** product re-fixes.
5. Never PASS unrun or single-path checks.

## Layout
- Areas: `01_unit_integration`, `02_web_api`, `03_security_quality`, `04_infra_deploy`
- Day files: `test_sheet.xlsx`, `pass.md`, `fail.md`, `risk.md`, `results.tsv`
- Root Excel: `qa/master_test_sheet.xlsx`
- Map: `qa/config/test_map.json`
