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

## When to use what

| Need | Use |
|------|-----|
| Map several discrete values to one action | `s.case(['c', 'a'], func) — list keys expand to one case per item` |
| Match an inclusive numeric span | `s.case(closed_range(1, 5), func)` |
| Run the next case too (fall-through) | `s.case(key, func, fallthrough=True)` |
| Get the matched case's return value | `s.result, after the with block exits` |
| Handle 'nothing matched' | `s.default(func), registered last` |
| Match a key but do nothing | `s.case(key, lambda: None)` |

## API overview

### The switch block

The context manager that gives Python an explicit switch statement. Use it in a `with` block, register cases, then read `result`.


- `switch`: An explicit switch statement for Python, implemented as a context manager

### Range helpers

Helpers for mapping ranges of values to a single case.


- `closed_range`: Create a closed range for a case: both `start` and `stop` are included

## Gotchas

1. Cases execute on block exit, not at registration: case()/default() only register; the matched function runs in __exit__, and s.result is only readable after the with block (reading it inside raises).
2. Case functions take no parameters — bind arguments with a lambda: s.case('b', lambda: process(val)). Passing process(val) calls it immediately and registers its return value.
3. default() ordering is not enforced: a default registered before a matching case runs as well. Always register default() last.
4. Adjacent closed_range cases overlap (closed_range(1, 5) and closed_range(5, 9) both contain 5) and raise a duplicate-case ValueError — follow closed_range(1, 5) with closed_range(6, 9).
5. Keys are matched with == and stored in a set: they must be hashable, and equal-comparing keys (1 and True, 1 and 1.0) are duplicates.
6. If no case matches and no default() is registered, the block raises Exception on exit.
7. An exception raised inside the with block aborts the switch — it is re-raised and no case actions run.
8. fallthrough=None is reserved for internal use — pass only True or False.

## Best practices

- Register default() as the last statement in every switch block.
- Read s.result only after the with block exits; capture per-case data via lambdas or closures.
- Use closed_range(start, stop) for inclusive numeric spans and plain range() for half-open ones.
- Import from the package — from switchlang import switch, closed_range — never from the private __switchlang_impl module.

## End-to-end wiring

A complete, minimal switch — registration inside the `with` block, execution at block exit, result read after:

```python
from switchlang import switch, closed_range

action = get_action()

with switch(action) as s:
    s.case(['c', 'a'], create_account)              # several keys -> one action
    s.case('l', log_into_account)
    s.case('', lambda: None)                        # explicit "do nothing" case
    s.case(closed_range(1, 5), lambda: set_level(action))  # inclusive 1..5
    s.default(unknown_command)                      # ALWAYS register last

print(s.result)   # return value of whichever case ran — only valid here, after the block
```

## The execution model (this is what code generators get wrong)

`case()` and `default()` only **register** cases — nothing executes at those lines. The matched function (and any fall-through functions) run inside `__exit__` as the `with` block closes. Three consequences:

- Case functions take **zero parameters**. Bind data with a lambda or closure: `s.case('b', lambda: process(val, num))` — never `s.case('b', process(val, num))`, which would call the function immediately and register its return value.
- `s.result` is only readable **after** the block; reading it inside raises even when the case has already been registered and matched.
- Registration errors (duplicate key, non-callable action, empty list/range) raise at the `s.case(...)` line, but the "no case matched and no default" error raises at the block's closing line.

## Fall-through, from the usage side

Fall-through is opt-in per case. The next registered case then runs **whether or not its key matches**, continuing until a case without `fallthrough=True`. The last function executed supplies `result`:

```python
value = 2
with switch(value) as s:
    s.case(1, lambda: 'one')
    s.case(2, lambda: 'two', fallthrough=True)
    s.case(3, lambda: 'three')     # runs too (its key is never compared), then the chain stops
    s.default(lambda: 'other')

s.result  # 'three'
```

Pass only `True` or `False` — `fallthrough=None` is reserved for the library's internal list/range expansion.

## Keys: equality, hashability, ranges

Matching is plain `key == value`, and keys are stored in a `set`, so every key must be hashable and keys that compare equal are duplicates (`1` and `True`, `1` and `1.0` collide). A `list` or `range` key is expanded so each item becomes its own case for the same function. `closed_range(start, stop)` is inclusive on **both** ends — and because of that, adjacent closed ranges share their endpoint and raise the duplicate-case error: use `closed_range(1, 5)` with `closed_range(6, 9)`, not `closed_range(5, 9)`.

## When to reach for this vs `match`

`match` (3.10+) destructures by *shape*; `switchlang` dispatches on *values*. Prefer `switchlang` when you need opt-in fall-through, case lists built at runtime (`s.case(some_list, action)`), a captured return value (`s.result`), or Python 3.9 support. Prefer `match` for structural pattern matching on tuples/dataclasses/nested data. Remember: `import switchlang`, `pip install switchlang` — the repo name `python-switch` is not the import name.

## Fetching the docs as Markdown

Every page on the documentation site has a plain-Markdown twin: swap the `.html` extension for `.md` to get token-efficient source without the site chrome. For example https://mkennedy.codes/docs/python-switch/reference/switch.html is also available at https://mkennedy.codes/docs/python-switch/reference/switch.md. Prefer the `.md` form when reading these docs programmatically.


## Resources

- [Full documentation](https://mkennedy.codes/docs/python-switch/)
- [llms.txt](llms.txt) — Indexed API reference for LLMs
- [llms-full.txt](llms-full.txt) — Comprehensive documentation for LLMs
- [Source code](https://github.com/mikeckennedy/python-switch)
