# switch, dict, if/elif or match?

Python has three ordinary ways to dispatch on a value, and each one is right for something. This page sets them next to switchlang so you can pick on purpose.


# The short version

| You want to… | Reach for |
|----|----|
| Take data apart by shape (tuples, dataclasses, nested structures) | `match` |
| Look up one of a fixed set of values, nothing else | a `dict` |
| Branch on arbitrary conditions, not just equality | `if / elif / else` |
| Dispatch on values with ranges, shared actions, a captured result, duplicate checking and optional fall-through | [switch](../reference/switch.md#switchlang.switch) |


# A `dict` of functions

``` python
handlers = {1: method_on_one, 2: method_on_two, 3: method_three}
result = handlers.get(value, default_method)()
```

For a handful of simple keys this is hard to beat. It gets awkward when several keys share an action (each one is written out), when a key is a range (unrolled by hand), and when a key is accidentally repeated: a dict literal silently keeps the last value, so the earlier handler disappears with no error. switchlang raises on the duplicate the first time the block runs, and lists and ranges are one line each.

A dict also has no notion of "nothing matched." `.get()` with a default hides that; `[]` on a missing key raises `KeyError` with no sense of which switch failed. switchlang requires a [default()](../reference/switch.md#switchlang.switch.default) or raises with the value in the message.


# `if / elif / else`

``` python
if action == 'c' or action == 'a':
    result = create_account()
elif action == 'l':
    result = log_into_account()
elif action == 'a':
    result = update_availability()
else:
    unknown_command()
```

This is the most flexible option, because each branch can test anything, not just equality. It is also where two quiet bugs live. The `'a'` in the third branch is dead code, because the first branch already claims it, and nothing in Python will say so. And the `else` forgot to set [result](../reference/switch.md#switchlang.switch.result), which only matters on the branch nobody tests. switchlang turns the first into a `ValueError` at registration and makes the second impossible, because every case including the default contributes a result.

Use `if / elif` when the tests aren't equality tests. Use a switch when they are.


# `match`

Python 3.10's structural pattern matching is excellent at what it was built for: destructuring data by shape.

``` python
match event:
    case {'type': 'click', 'x': x, 'y': y}:
        handle_click(x, y)
    case {'type': 'key', 'code': code}:
        handle_key(code)
```

Compared with a value switch, it covers different ground:

- **No fall-through.** `match` arms are exclusive. switchlang's fall-through is opt-in per case.
- **Arms are syntax, not data.** You can't build `match` cases from a list at runtime. `s.case(some_list, action)` is a method call, so you can (see [Patterns](patterns.md#cases-built-from-data)).
- **The capture trap.** In a [case](../reference/switch.md#switchlang.switch.case) pattern, a bare name such as `case other:` doesn't compare against a variable named `other`; it binds a new one and matches everything. Keys in switchlang are values, so this can't happen.
- **No result capture.** `match` arms are blocks of statements. switchlang dispatches to callables and hands back the chosen one's return value as `s.result`.
- **Python version.** `match` needs 3.10 or newer. switchlang runs on 3.9 and newer.

If you are matching on structure, use `match`. If you are dispatching on values and want ranges, shared actions, a result and the validation described in [Errors and validation](errors.md), use switchlang.


# What switchlang is not

It is not faster than any of the above; a switch block does a little more work than a dict lookup, because it validates as it goes. It is not a language change, and it won't be recognized by tools that understand `match`. It is a small, readable library for the common case of "here is a value, here is what to do for each of its possibilities," written so that the code looks like that sentence.
