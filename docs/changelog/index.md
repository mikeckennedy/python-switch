# Changelog

All notable changes to **switchlang** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


# [Unreleased](https://github.com/mikeckennedy/python-switch/compare/v0.1.2...HEAD)


# [0.1.2](https://github.com/mikeckennedy/python-switch/compare/v0.1.1...v0.1.2) - 2026-06-11

This release brings switchlang's whole public-facing surface up to date -- a documentation site, a shipped type-hint contract, refreshed docs -- and fixes two correctness bugs in the public API ([\#13](https://github.com/mikeckennedy/python-switch/issues/13), [\#14](https://github.com/mikeckennedy/python-switch/issues/14)).


## Added

- **Type information now ships with the package.** A `py.typed` marker makes the hints public API, so switchlang's signatures type-check and autocomplete in IDEs and type checkers. Every public signature is annotated -- `case() -> bool`, `__enter__() -> switch`, `__exit__(...)`, `result -> Any`, and `closed_range(...) -> range` -- using modern, Python 3.9-safe syntax (`from __future__ import annotations`). ([\#13](https://github.com/mikeckennedy/python-switch/issues/13))
- **Documentation site** at [mkennedy.codes/docs/python-switch](https://mkennedy.codes/docs/python-switch/), built with [Great Docs](https://github.com/posit-dev/great-docs) (Quarto): a landing page plus an API reference for [switch](../reference/switch.md#switchlang.switch) and [closed_range](../reference/closed_range.md#switchlang.closed_range). Includes `scripts/build_docs.py` and `scripts/serve_docs.py`. ([\#13](https://github.com/mikeckennedy/python-switch/issues/13))
- **[closed_range()](../reference/closed_range.md#switchlang.closed_range) now validates its step.** A `step` less than 1 raises a clear `ValueError` instead of surfacing a raw `range` error (for `step=0`) or silently producing an empty range (for a negative step). ([\#14](https://github.com/mikeckennedy/python-switch/issues/14))
- `uv add switchlang` installation instructions alongside pip. ([\#13](https://github.com/mikeckennedy/python-switch/issues/13))


## Changed

- **Packaging modernized** to `pyproject.toml` + hatchling: the version is read from package metadata, a `[dev]` extra is provided, Python 3.9-3.15 classifiers and a `Typing :: Typed` classifier are declared, and full project URLs (docs, repository, issues, PyPI, funding) are published. ([\#13](https://github.com/mikeckennedy/python-switch/issues/13))
- **[case()](../reference/switch.md#switchlang.switch.case) now always returns `bool`.** It previously returned `None` on a scalar no-match but `False` on a list no-match; the return value is now a consistent `bool`. ([\#13](https://github.com/mikeckennedy/python-switch/issues/13))
- Tooling: ruff pinned to `target-version = "py39"` to match `requires-python = ">=3.9"`. ([\#13](https://github.com/mikeckennedy/python-switch/issues/13))


## Fixed

- **`closed_range(start, stop, step)` no longer overshoots `stop` when `step > 1`.** The inclusive bound was built as `range(start, stop + step, step)`, which added a full extra step -- e.g. `closed_range(1, 6, 2)` yielded `[1, 3, 5, 7]`, letting `7` (a value outside the stated range) silently match the case. The bound is now computed as `stop + 1`, so values never pass `stop` while `stop` is still included when a step lands on it exactly (`closed_range(1, 7, 2)` -\> `1, 3, 5, 7`). ([\#14](https://github.com/mikeckennedy/python-switch/issues/14))
- **`.result` no longer breaks for matched cases that return an always-equal object.** The "no result" sentinel was compared with `==`, so a returned object with a permissive `__eq__` (a NumPy array is the real-world case) made `.result` raise *"No result has been computed"* even though a result existed. The sentinel is now compared by identity (`is`). ([\#14](https://github.com/mikeckennedy/python-switch/issues/14))


## Documentation

- **README refreshed:** version and docs badges, a prominent link to the documentation site, an honest feature list ("Validates that case actions are callable", replacing an inaccurate signature-verification claim), a new `s.result` bullet, a new "Fall-through and results" section, a new "Why not just `match`?" section, a [closed_range](../reference/closed_range.md#switchlang.closed_range) usage example, and f-strings throughout. ([\#13](https://github.com/mikeckennedy/python-switch/issues/13))
- **Docstrings rewritten to render as the API reference:** [switch](../reference/switch.md#switchlang.switch) is described as a context manager; [default()](../reference/switch.md#switchlang.switch.default) documents that ordering is not enforced (register it last); [case()](../reference/switch.md#switchlang.switch.case) documents its return contract, the `ValueError`s it raises, and the internal no-match sentinel; [result](../reference/switch.md#switchlang.switch.result) documents that the last function executed wins under fall-through; and [closed_range](../reference/closed_range.md#switchlang.closed_range) is documented as returning a `range` object (not a "generator") with its step semantics and `ValueError`. ([\#13](https://github.com/mikeckennedy/python-switch/issues/13))


# [0.1.1](https://github.com/mikeckennedy/python-switch/releases/tag/v0.1.1) - 2025-09-11


## Changed

- Standardized string literals on double quotes across the codebase and added an initial round of type annotations, including a fix for a potential type warning on `s.result`.


# [0.1.0](https://pypi.org/project/switchlang/0.1.0/) - 2020-12-10


## Added

- Initial public release of switchlang on PyPI: an explicit [switch](../reference/switch.md#switchlang.switch) block for Python built on the `with` statement, with default cases, duplicate-case detection, list/range cases, opt-in fall-through, and the [closed_range](../reference/closed_range.md#switchlang.closed_range) helper.
