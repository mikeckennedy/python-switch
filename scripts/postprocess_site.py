#!/usr/bin/env python3
"""Post-process the mirrored docs/ site after a Great Docs build.

Run automatically by scripts/build_docs.py; can also be run by hand:

    uv run python scripts/postprocess_site.py [site_dir]   # default: repo-root docs/

Two fix-ups for Great Docs 0.17.0 gaps:

1. Version badge (below).
2. llms.txt lists only the API reference because Great Docs writes it before the User Guide is
   wired in; `append_llms_user_guide` adds the guide pages and skill links.

Why the badge rewrite exists
----------------------------
Great Docs puts a version badge in the navbar of every page:

    <span class="version-badge" title="Released YYYY-MM-DD">vX.Y.Z</span>

The version and date come from the repo's **latest GitHub Release** at build time
(great_docs/core.py writes `_package_meta.json` from `_fetch_github_releases(...)`,
and great_docs/assets/post-render.py injects the badge from it). They do *not* come
from the package. Our release order is build docs -> commit -> tag -> GitHub release,
so a site built for a new version shows the *previous* version until it is rebuilt
after the release. There is no CLI flag or config key to change the source.

So after mirroring the site we rewrite every badge from local sources of truth:
`[project].version` in pyproject.toml and the matching dated heading
(`## [X.Y.Z] - YYYY-MM-DD`) in CHANGELOG.md. If a Great Docs upgrade changes the
badge markup the replacement count drops to 0, which is reported as a warning.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import tomllib

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = REPO_ROOT / 'pyproject.toml'
CHANGELOG = REPO_ROOT / 'CHANGELOG.md'
GREAT_DOCS_YML = REPO_ROOT / 'great-docs.yml'
DEFAULT_SITE = REPO_ROOT / 'docs'

# The badge Great Docs' post-render injects into <span class="navbar-title">.
_VERSION_BADGE = re.compile(r'<span class="version-badge"[^>]*>[^<]*</span>')


def project_version(pyproject: Path = PYPROJECT) -> str:
    """Return the static `[project].version` from pyproject.toml."""
    return tomllib.loads(pyproject.read_text(encoding='utf-8'))['project']['version']


def release_date(version: str, changelog: Path = CHANGELOG) -> str | None:
    """Return the YYYY-MM-DD date of the `## [version] - date` heading in CHANGELOG.md, or None."""
    if not changelog.is_file():
        return None
    text = changelog.read_text(encoding='utf-8')
    m = re.search(rf'^## \[{re.escape(version)}\] - (\d{{4}}-\d{{2}}-\d{{2}})', text, re.MULTILINE)
    return m.group(1) if m else None


def version_badge() -> str:
    """Build the badge HTML for the current project version."""
    version = project_version()
    date = release_date(version)
    if date is None:
        print(
            f'WARNING: no dated "## [{version}] - YYYY-MM-DD" heading in {CHANGELOG.name}; badge gets no release date',
            file=sys.stderr,
        )
        return f'<span class="version-badge">v{version}</span>'
    return f'<span class="version-badge" title="Released {date}">v{version}</span>'


def rewrite_version_badges(site_dir: Path, badge: str) -> int:
    """Replace every version badge under `site_dir` with `badge`; return the number replaced."""
    count = 0
    for page in sorted(site_dir.rglob('*.html')):
        text = page.read_text(encoding='utf-8')
        new_text, n = _VERSION_BADGE.subn(badge, text)
        if n:
            page.write_text(new_text, encoding='utf-8')
            count += n
    return count


def _site_url() -> str:
    """Return `site_url` from great-docs.yml (with its trailing slash), or '' if unset."""
    m = re.search(r'(?m)^\s*site_url:\s*["\']?([^"\'\n]+)', GREAT_DOCS_YML.read_text(encoding='utf-8'))
    return m.group(1).strip() if m else ''


def _user_guide_outline() -> list[tuple[str, list[str]]]:
    """Return [(section title, [page stem, ...]), ...] from the `user_guide:` block of great-docs.yml."""
    text = GREAT_DOCS_YML.read_text(encoding='utf-8')
    block = re.search(r'(?ms)^user_guide:\n(.*?)(?=^\S|\Z)', text)
    if not block:
        return []
    outline: list[tuple[str, list[str]]] = []
    for m in re.finditer(r'^\s*-\s+section:\s*["\']?(.+?)["\']?\s*$|^\s*-\s+(\S+?)\.qmd\s*$', block.group(1), re.M):
        if m.group(1):
            outline.append((m.group(1), []))
        elif m.group(2) and outline:
            outline[-1][1].append(m.group(2))
    return outline


def _page_title(md_file: Path, fallback: str) -> str:
    """Return the first `# Heading` of a rendered Markdown companion page, or `fallback`."""
    if md_file.is_file():
        for line in md_file.read_text(encoding='utf-8').splitlines():
            if line.startswith('# '):
                return line[2:].strip()
    return fallback


def append_llms_user_guide(site_dir: Path) -> bool:
    """Append the User Guide pages (and skill/full-context links) to llms.txt.

    Great Docs (0.17.0) writes llms.txt before it wires the User Guide into the site, so the
    file lists only the API reference even though llms-full.txt contains the guide text.
    Returns True if llms.txt was changed.
    """
    llms = site_dir / 'llms.txt'
    if not llms.is_file():
        return False
    text = llms.read_text(encoding='utf-8')
    if '### User Guide' in text:
        return False
    outline = _user_guide_outline()
    if not outline:
        return False

    base = _site_url()
    lines = ['### User Guide', '']
    for section, pages in outline:
        lines.extend([f'#### {section}', ''])
        for stem in pages:
            title = _page_title(site_dir / 'user-guide' / f'{stem}.md', stem)
            lines.append(f'- [{title}]({base}user-guide/{stem}.html)')
        lines.append('')
    lines.extend(
        [
            '### Agent Skill and Full Context',
            '',
            f'- [Agent Skill (SKILL.md)]({base}skill.md): compact guide, decision table and gotchas for AI agents',
            f'- [Full Documentation (llms-full.txt)]({base}llms-full.txt): API reference and User Guide in one file',
            '',
        ]
    )
    llms.write_text(text.rstrip() + '\n\n' + '\n'.join(lines), encoding='utf-8')
    return True


def main(argv: list[str]) -> int:
    site_dir = Path(argv[1]).resolve() if len(argv) > 1 else DEFAULT_SITE
    if not site_dir.is_dir():
        print(f'site directory not found: {site_dir}', file=sys.stderr)
        return 1

    badge = version_badge()
    count = rewrite_version_badges(site_dir, badge)
    print(f'Rewrote {count} version badge(s) in {site_dir} -> {badge}')
    if count == 0:
        print(
            'WARNING: no version badges found. Either the repo has no GitHub Releases (Great Docs then emits '
            'no badge) or a Great Docs upgrade changed the badge markup; check _VERSION_BADGE.',
            file=sys.stderr,
        )
    if append_llms_user_guide(site_dir):
        print('llms.txt: appended User Guide and skill links')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
