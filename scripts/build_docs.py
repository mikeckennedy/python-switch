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
CHANGELOG = REPO_ROOT / 'CHANGELOG.md'  # hand-maintained, single source of truth
CHANGELOG_SECTION = REPO_ROOT / 'changelog'  # great-docs "Changelog" section (gitignored, staged here)


def stage_changelog() -> None:
    """Render the repo-root CHANGELOG.md into the great-docs "Changelog" section.

    Great Docs has no "source the changelog from a file" option — its built-in
    changelog is generated from GitHub Releases (disabled in great-docs.yml).
    So we treat CHANGELOG.md as the single source of truth and stage it into a
    one-page section (changelog/index.qmd) on every build. The leading "# Changelog"
    H1 is dropped in favor of a real page title + a version-level table of contents.
    """
    if not CHANGELOG.is_file():
        print(f'CHANGELOG.md not found at {CHANGELOG}, skipping changelog section', file=sys.stderr)
        return

    body = CHANGELOG.read_text(encoding='utf-8')
    lines = body.splitlines()
    if lines and lines[0].lstrip().startswith('# '):  # drop the top-level "# Changelog" heading
        lines = lines[1:]
    body = '\n'.join(lines).lstrip('\n')

    front_matter = '---\ntitle: "Changelog"\ntoc: true\ntoc-depth: 2\n---\n\n'
    CHANGELOG_SECTION.mkdir(parents=True, exist_ok=True)
    (CHANGELOG_SECTION / 'index.qmd').write_text(front_matter + body, encoding='utf-8')
    print(f'Staged CHANGELOG.md -> {CHANGELOG_SECTION / "index.qmd"}')


def main() -> int:
    stage_changelog()

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
