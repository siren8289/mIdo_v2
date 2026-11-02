# QA Agent (single)

One orchestrating QA agent + one skill (`tsv-qa`).

Responsibilities in order: plan from TSV → design/bind assertions → execute via scripts → risk audit → report.

- Layout: `qa/results/<area>/<section>/<YYYY-MM-DD>/` with five English-named files
- Areas: `01_unit_integration`, `02_web_api`, `03_security_quality`, `04_infra_deploy`
- Root aggregate TSV: `qa/master_test_sheet.tsv` only (no root Excel)
- Dual verify; scripts for runs; AI for new TC / impact / hard failures only
- Report body Korean; paths and IDs English
