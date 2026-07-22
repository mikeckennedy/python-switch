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
