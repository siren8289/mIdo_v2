#!/usr/bin/env python3
"""Opt-in, non-destructive global skill installer. Does not install global hooks."""
import argparse
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
HOME = Path.home()


def main():
    parser = argparse.ArgumentParser(description="Share the TSV QA skill across supported AI tools")
    parser.add_argument("--apply", action="store_true", help="Actually copy; without it only preview")
    parser.add_argument("--force", action="store_true", help="Replace existing identical-named skill/agent (with backup)")
    args = parser.parse_args()
    destinations = [
        (BASE / '.agents/skills/tsv-qa', HOME / '.agents/skills/tsv-qa', 'Codex'),
        (BASE / '.agents/skills/tsv-qa', HOME / '.gemini/config/skills/tsv-qa', 'Antigravity'),
        (BASE / '.claude/skills/tsv-qa', HOME / '.claude/skills/tsv-qa', 'Claude Code'),
        (BASE / '.agents/skills/tsv-qa', HOME / '.grok/skills/tsv-qa', 'Grok Build'),
    ]
    destinations += [(p, HOME / '.claude/agents' / p.name, 'Claude Subagent')
                     for p in sorted((BASE / '.claude/agents').glob('*.md'))]
    for src, target, label in destinations:
        if target.exists() and not args.force:
            print(f'[SKIP existing] {label}: {target} (use --force only after review)')
            continue
        print(f"[{'INSTALL' if args.apply else 'PREVIEW'}] {label}: {src} -> {target}")
        if not args.apply:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            backup = target.with_name(target.name + '.previous')
            if backup.exists():
                raise RuntimeError(f'Backup already exists; resolve manually: {backup}')
            target.rename(backup)
        if src.is_dir():
            shutil.copytree(src, target)
        else:
            shutil.copy2(src, target)
    if not args.apply:
        print('\nPreview only. Rerun with --apply to install.')
    print('\nGlobal skills are reusable, but do not automatically install tests or CI in every repository.')


if __name__ == '__main__':
    main()
