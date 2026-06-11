---
name: switchlang
description: >
  Adds switch blocks to the Python language. Use when writing Python code that uses the switchlang package.
license: MIT
compatibility: Requires Python >=3.9.
---

# switchlang

Adds switch blocks to the Python language.

## Installation

```bash
pip install switchlang
```

## API overview

### The switch block

The context manager that gives Python an explicit switch statement. Use it in a `with` block, register cases, then read `result`.


- `switch`: An explicit switch statement for Python, implemented as a context manager

### Range helpers

Helpers for mapping ranges of values to a single case.


- `closed_range`: Create a closed range for a case: both `start` and `stop` are included

## Resources

- [Full documentation](https://mkennedy.codes/docs/python-switch/)
- [llms.txt](llms.txt) — Indexed API reference for LLMs
- [llms-full.txt](llms-full.txt) — Comprehensive documentation for LLMs
- [Source code](https://github.com/mikeckennedy/python-switch)
