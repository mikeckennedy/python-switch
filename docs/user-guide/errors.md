# Errors and validation

A switch statement is a list of claims: these are the keys, these are the actions, this is the fallback. switchlang checks those claims and raises when one is wrong, instead of quietly skipping a case or running the wrong one. This page lists what it checks and when each check runs.


# What is checked

| Situation | Raised | When |
|----|----|----|
| The same key registered twice (including items of lists and ranges, and keys that compare equal such as `1` and `True`) | `ValueError` | At registration |
| The action is `None` | `ValueError` | At registration |
| The action is not callable (often a function that was *called* instead of passed) | `ValueError` | At registration |
| An empty list as the key | `ValueError` | At registration |
| An unhashable key such as a dict | `TypeError` | At registration |
| [closed_range](../reference/closed_range.md#switchlang.closed_range) with `start >= stop` or `step < 1` | `ValueError` | When [closed_range()](../reference/closed_range.md#switchlang.closed_range) is called |
| No case matched and no [default()](../reference/switch.md#switchlang.switch.default) was registered | `Exception` | At block exit |
| Your code raised inside the block | that exception | At block exit, before any action runs |
| A case action raised | that exception | At block exit, from the action |

"At registration" means on the `s.case(...)` line itself, inside the block. The exception leaves the block immediately, and no action runs.


# Seeing them


``` python
from switchlang import switch, closed_range


def duplicate_key():
    with switch('a') as s:
        s.case('a', lambda: 1)
        s.case('a', lambda: 2)


def action_is_none():
    with switch('a') as s:
        s.case('a', None)


def action_not_callable():
    with switch('a') as s:
        s.case('a', 'not a function')


def empty_list():
    with switch('a') as s:
        s.case([], lambda: 1)


def nothing_matched():
    with switch('z') as s:
        s.case('a', lambda: 1)


def backwards_range():
    closed_range(5, 1)


checks = [duplicate_key, action_is_none, action_not_callable, empty_list, nothing_matched, backwards_range]

for check in checks:
    try:
        check()
    except Exception as e:
        print(f'{check.__name__:20} {type(e).__name__}: {e}')
```


    duplicate_key        ValueError: Duplicate case: a
    action_is_none       ValueError: Action for case cannot be None.
    action_not_callable  ValueError: Func must be callable.
    empty_list           ValueError: You cannot pass an empty collection as the case. It will never match.
    nothing_matched      Exception: Value does not match any case and there is no default case: value z
    backwards_range      ValueError: Start must be less than stop.


# Why "no match" is an error

A dict lookup with `.get()` returns `None` when the key is missing. An `if / elif` chain with no `else` does nothing. Both are easy to write and easy to not notice. switchlang treats a value that matches nothing, with no default to catch it, as a mistake in the switch, and raises a plain `Exception` naming the value. If silence is what you want, say so:

``` python
s.default(lambda: None)
```


# Exceptions inside the block

If your own code raises while the block is open, the switch is abandoned and the exception propagates unchanged. No case action runs, not even one that had already matched. See [How a switch block runs](how-it-works.md#when-the-block-raises).

If a case *action* raises, that happens at block exit, when the action runs. The exception propagates from the end of the `with` statement, and `s.result` is not set.


# Why these are errors and not warnings

Most of these mistakes have the same shape: code that looks right, imports fine, and does the wrong thing on one input. A duplicated key in an `if / elif` chain is dead code that nothing reports. A function called instead of passed produces a value where an action should be. By raising at the point of registration, switchlang turns each of them into a traceback on the first run of the block, pointing at the line to fix.
