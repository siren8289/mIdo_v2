# Always-on TSV QA (Claude Code) V3

Apply `.claude/skills/tsv-qa/SKILL.md` and `qa-policy.md` / `AGENTS.md` on every change and **before every commit/push**.
Source: `qa/input/testcases.tsv` (from `qa/input/atomic_testcases_872.xlsx`).
Run `python3 qa/run.py`. CI `qa-gate` runs on every push/PR. Local: `git config core.hooksPath .githooks`.
