#!/usr/bin/env python3
"""Build the docs with Great Docs and mirror the static site into the committed docs/ folder.

The great-docs/ build directory is ephemeral (regenerated every build and gitignored).
The mirrored repo-root docs/ folder is what gets committed and served by nginx at
https://mkennedy.codes/docs/python-switch/.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent  # pyproject.toml + great-docs.yml live here
SITE = REPO_ROOT / 'great-docs' / '_site'
DEST = REPO_ROOT / 'docs'


def main() -> int:
    # Prefer the great-docs entry point that lives next to this interpreter (the venv's).
    great_docs = Path(sys.executable).with_name('great-docs')
    cmd = [str(great_docs) if great_docs.exists() else 'great-docs', 'build']
    if subprocess.run(cmd, cwd=REPO_ROOT).returncode != 0:
        return 1

    if not SITE.is_dir():
        print(f'build output missing: {SITE}', file=sys.stderr)
        return 1

    # Full replace so deleted pages don't linger in the committed site.
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(SITE, DEST)

    file_count = sum(1 for p in DEST.rglob('*') if p.is_file())
    print(f'Mirrored -> {DEST} ({file_count} files)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
