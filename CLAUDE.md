# Agent guide: switchlang (python-switch)

Guidance for AI agents working in this repository. `GEMINI.md` and `AGENTS.md`
are symlinks to this file — edit this one.

## What this is

`switchlang` adds an explicit **switch statement to Python without changing the
language**. It is implemented as a context manager: you open a `with switch(value)`
block, register cases as method calls, and read the matched case's return value
from `s.result`. The whole library is ~200 lines with **zero runtime dependencies**.

- **Repo name** is `python-switch`; the **PyPI / import name** is `switchlang`.
  Don't confuse the two — `import switchlang`, `pip install switchlang`.
- The package ships type hints and a `py.typed` marker (PEP 561). It is
  `Typing :: Typed`.
- **The default git branch is `master`, not `main`.** Several tools (and
  `great-docs.yml`) hard-code this.

## Repository layout

| Path | What it is |
|------|------------|
| [switchlang/__init__.py](switchlang/__init__.py) | Public package: re-exports `switch` and `closed_range`, sets `__version__`/`__author__`/`__all__`. |
| [switchlang/__switchlang_impl.py](switchlang/__switchlang_impl.py) | **The entire implementation** — `switch` class and `closed_range()`. Make code changes here. |
| [switchlang/py.typed](switchlang/py.typed) | PEP 561 marker so type checkers read our hints. |
| [tests/test_core.py](tests/test_core.py) | The whole test suite (29 `unittest`-style tests). |
| [pyproject.toml](pyproject.toml) | Packaging (hatchling), metadata, version, `[dev]` extra. |
| [ruff.toml](ruff.toml) | Lint + format config. |
| [great-docs.yml](great-docs.yml) | Docs site config (Great Docs / Quarto). |
| [scripts/build_docs.py](scripts/build_docs.py) | Builds docs and mirrors them into `docs/`. |
| [scripts/serve_docs.py](scripts/serve_docs.py) | Local preview that mimics the nginx subpath. |
| [docs/](docs/) | **Generated** static site (committed, served at `mkennedy.codes/docs/python-switch`). Do not hand-edit. |
| [README.md](README.md) | The narrative/marketing docs and rationale. Keep in sync with behavior. |

Generated / ignored artifacts you should not edit or commit by hand: `docs/`
(regenerate it), `great-docs/` (ephemeral build dir, gitignored), `dist/`,
`*.egg-info/`, `venv/`.

## The public API and its semantics

Only two names are public (`switchlang.__all__`): **`switch`** and **`closed_range`**.

```python
from switchlang import switch, closed_range

with switch(value) as s:
    s.case('a', process_a)                       # key == value -> run process_a
    s.case(['v', 'b'], view_bookings)            # list key: each item is a case
    s.case(range(1, 6), handler)                 # range key: each item is a case
    s.case(closed_range(1, 5), handler)          # inclusive range: 1,2,3,4,5
    s.case(2, do_two, fallthrough=True)          # opt into running the next case too
    s.default(unknown_command)                   # runs if nothing else matched
print(s.result)                                  # return value of the executed case
```

Behaviors that are easy to get wrong — preserve all of these (they are pinned by tests):

- **Cases run on block exit, not at registration.** `case()`/`default()` only
  *register*; the matched function(s) execute in `__exit__`. So `s.result` is only
  valid *after* the `with` block. Reading it inside the block raises.
- **Matching is equality-based** (`key == value`). Keys are also stored in a `set`,
  so case keys must be **hashable**. Any hashable value works as a key, including
  `None` and arbitrary objects.
- **`default()` is just a case** keyed on a private sentinel, and **ordering is not
  enforced**: a default registered *before* a matching case will also run. **Always
  register `default()` last.**
- **`result` uses identity, not equality, against its "no result" sentinel.** A
  computed result with a permissive `__eq__` (e.g. a NumPy array) must not be
  mistaken for "nothing computed." `None` is a valid computed result and is
  distinct from "not computed."
- **`case()` returns `bool`** — `True` if the case (or any item of a list/range
  key) matched.
- **Fall-through is opt-in** per case via `fallthrough=True`; the next registered
  case then runs whether or not its key matches, and so on until a case without
  fall-through. When falling through, `result` is the **last** function executed.
  The `fallthrough=None` value is **reserved for internal recursion** (list/range
  expansion) and must not be used by callers.
- **`closed_range(start, stop, step=1)`** is inclusive on **both** ends and never
  overshoots `stop`: `closed_range(1, 5)` -> `1,2,3,4,5`; `closed_range(1, 6, 2)`
  -> `1,3,5`; `closed_range(1, 7, 2)` -> `1,3,5,7`. Note adjacent closed ranges
  **overlap** (`closed_range(1,5)` and `closed_range(5,9)` both contain 5) and will
  raise a duplicate-case error.

Validation (all raise on registration/exit):

- Duplicate case key -> `ValueError`.
- `func` that is `None` or not callable -> `ValueError`.
- Empty list/range key (`[]`) -> `ValueError` (it could never match).
- `closed_range` with `start >= stop` or `step < 1` -> `ValueError`.
- No case matched **and** no `default()` registered -> `Exception` on block exit.
- An **exception raised inside the `with` block** propagates and aborts the switch:
  `__exit__` re-raises it before any case actions run, so for a normal exception
  **no case actions run**. (One sharp edge — see *Implementation notes* — the guard
  is a truthiness check, so an exception whose `__bool__` is falsy slips past it.)

## Implementation notes (don't refactor naively)

- The implementation lives in a deliberately **private module**,
  `__switchlang_impl.py` (leading dunder); `__init__.py` re-exports `switch` and
  `closed_range`. Import via the package (`from switchlang import ...`), never the
  impl module directly.
- The `switch` class's `__no_result` and `__default` are **name-mangled class
  attributes** assigned `uuid.uuid4()` at class-load time (mangled to
  `_switch__no_result` / `_switch__default`) — unique, opaque sentinels. Don't
  rename the class or hoist these to module level, and **keep the `result` check
  identity-based** (`is`, not `==`); that identity check is what stops a result with
  a permissive `__eq__` (e.g. a NumPy array) from being read as "no result."
- `__exit__` guards exception re-raise with `if exc_val:` (truthiness), not
  `is not None`. For normal exceptions this is correct, but an exception whose
  `__bool__`/`__len__` is falsy slips past the guard and the matched case runs
  before the exception propagates. A latent sharp edge — switch to
  `if exc_val is not None:` if you want the guarantee to be absolute.

## Development workflow

There is a **local, gitignored** uv-managed `venv/` — it is **not** in the repo, so
on a fresh checkout it is absent (and even on the maintainer's machine its symlinks may
be broken). **Never rely on `venv/bin/python` existing**; use `uv run`, which provisions
the environment on demand. Note that the tracked [.vscode/tasks.json](.vscode/tasks.json)
and [.vscode/launch.json](.vscode/launch.json) (Build / Preview Docs) hard-code
`venv/bin/python` and `venv/bin/great-docs`, so those IDE configs only work once such a
venv exists at that path — prefer `uv run` from the CLI.

```bash
# Run the test suite — fast path, no extra deps (tests are unittest-based):
uv run python -m unittest discover -s tests

# Or with pytest + the full dev environment (pulls in great-docs and its deps):
uv run --extra dev pytest -q

# Lint and format (config in ruff.toml):
uvx ruff check .
uvx ruff format .
```

Coding constraints — match the existing style:

- **Python 3.9+** is supported (classifiers go through 3.15). **Do not use syntax
  that breaks 3.9.** The impl uses `from __future__ import annotations` so it can
  write modern annotation syntax (`set[Any]`, `X | None`) while still importing on
  3.9. Ruff's `target-version` is pinned to `py39` to enforce this.
- Ruff config: **line length 120**, **single-quoted** strings, import sorting on
  (`I`), error/pyflakes rules (`E`, `F`), McCabe max complexity **10**.
- Keep the public API fully type-hinted (the package is `py.typed`). Note **no static
  type checker is wired into the project** — ruff only does lint/format/import-sort
  (`E`/`F`/`I`). Validate hints ad hoc if you want, e.g. `uvx mypy switchlang` or
  `uvx ty check switchlang`; there is no CI gate for types.
- When you change behavior, update **all three** places that document it:
  the **docstrings** in `__switchlang_impl.py` (source of the API reference),
  the **README**, and the **tests**. Then rebuild the docs.

## Versioning and release

- The version of record is `[project].version` in [pyproject.toml](pyproject.toml)
  (currently `0.1.2`). `__version__` is read at runtime from installed package
  metadata via `importlib.metadata`, falling back to `'0.0.0'` when not installed.
  Because it reflects *installed* metadata, after a bump you must reinstall
  (`uv pip install -e .`) before `__version__` or the introspected docs show the new
  number. `uv.lock` is gitignored, so there is no committed lockfile.
- Build backend is **hatchling**; the wheel packages the `switchlang/` directory.
- The changelog ([docs/changelog.md](docs/changelog.md)) is generated from GitHub
  Releases — don't hand-maintain it.

## Documentation pipeline

Docs are built with **Great Docs** (Quarto) and **dynamically introspect** the
installed package, so the docstrings in `__switchlang_impl.py` are the real source
of the API reference. The flow:

1. `scripts/build_docs.py` runs `great-docs build` (output -> `great-docs/_site`,
   which is ephemeral/gitignored) and **mirrors it into the committed `docs/`
   folder** (full replace, so deleted pages don't linger).
2. `scripts/serve_docs.py` serves `docs/` locally on port **8099** under the
   `/docs/python-switch` subpath to mirror production nginx and catch
   absolute-path asset bugs.
3. Production serves the committed `docs/` at `https://mkennedy.codes/docs/python-switch/`.

`great-docs.yml` has documented gotchas (subpath `site_url` needs a trailing
slash; SEO `canonical.base_url` must be set explicitly or the sitemap points at
the wrong domain; `mcp.enabled` is disabled; `source.branch` is `master`). The
generated site also includes agent-skill descriptors under
[docs/.well-known/](docs/.well-known/) and `llms.txt`/`llms-full.txt` — these are
**build output** (produced from the docstrings and `great-docs.yml`), so edit the
sources and rebuild rather than hand-editing them.

## Quick checklist for a typical change

1. Edit [switchlang/__switchlang_impl.py](switchlang/__switchlang_impl.py).
2. Update/extend [tests/test_core.py](tests/test_core.py) and run
   `uv run python -m unittest discover -s tests`.
3. Keep docstrings + [README.md](README.md) in sync with the new behavior.
4. `uvx ruff format . && uvx ruff check .`
5. If docs-visible, rebuild: `uv run --extra dev python scripts/build_docs.py`.
6. Bump `[project].version` in [pyproject.toml](pyproject.toml) if releasing.
