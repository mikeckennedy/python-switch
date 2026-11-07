# switchlang
[![](https://img.shields.io/pypi/v/switchlang.svg)](https://pypi.org/project/switchlang/)
[![](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![](https://img.shields.io/badge/docs-mkennedy.codes-brightgreen.svg)](https://mkennedy.codes/docs/python-switch/)
[![](https://img.shields.io/pypi/l/switchlang.svg)](https://github.com/mikeckennedy/python-switch/blob/master/LICENSE)
[![](https://img.shields.io/pypi/dm/switchlang.svg)](https://pypi.org/project/switchlang/)


**A real switch statement for Python. No new syntax, no compiler patches, no
dependencies. Just a `with` block.**

Python never got a `switch`. Every few years someone proposes one, the thread
runs to a few hundred messages, and we all go back to writing `if / elif / elif /
elif / else`. switchlang takes a different road: it builds the switch out of a
tool Python already has, the context manager, and hands you something that reads
like the statement you wished for.

```python
from switchlang import switch

with switch(command) as s:
    s.case('a', add_item)
    s.case('r', remove_item)
    s.case(['q', 'x'], quit_app)
    s.default(unknown_command)

print(s.result)   # whatever the chosen function returned
```

Full documentation lives at
**[mkennedy.codes/docs/python-switch](https://mkennedy.codes/docs/python-switch/)**:
a [user guide](https://mkennedy.codes/docs/python-switch/user-guide/getting-started.html)
whose examples run at build time, and the API reference.

## Installation

```bash
pip install switchlang
# or
uv add switchlang
```

Python 3.9 or newer. The whole library is about 200 lines with zero runtime
dependencies, and it ships type hints (`py.typed`), so your editor knows exactly
what `s.case` and `s.result` are.

## The problem, told as a story

Picture a small command-line app. A menu prints, the user types a letter, and
something happens. The first version has three commands and fits in your head:

```python
if action == 'c':
    create_account()
elif action == 'l':
    log_into_account()
else:
    unknown_command()
```

Then the app grows. Two letters should open the same screen. A range of digits
sets a difficulty level. One command should return a value you need afterwards.
Somebody adds a shortcut and accidentally reuses a letter that was already taken,
and nobody notices for a month because that branch sits below the one that steals
its input.

Every language with a `switch` solves this with a construct whose *shape* tells
you what it does: here is the value, here are the keys, here is what happens for
each. Python asks you to rebuild that shape by hand every time, with `if` chains
or a dict of functions. switchlang gives the shape a name.

## Your first switch, step by step

```python
from switchlang import switch

def main():
    num = 7
    val = input('Enter a character, a, b, c or any other: ')

    with switch(val) as s:
        s.case('a', process_a)
        s.case('b', lambda: process_with_data(val, num, 'other values still'))
        s.default(process_any)

def process_a():
    print('Found A!')

def process_any():
    print('Found Default!')

def process_with_data(*value):
    print(f'Found with data: {value}')

main()
```

Three things are happening, and one of them is the key to the whole library.

1. **`switch(val)` opens the block** and remembers the value you want to test.
2. **Each `s.case(key, func)` registers a case.** The key is compared with `==`
   against the value. The function is *not* called yet. It is filed away.
3. **The matched function runs when the block exits.** That is the trick. A
   `with` statement has a well-defined end, and switchlang uses that moment to
   execute whatever matched. Register everything first, run once at the end.

Notice the `lambda` on the `'b'` case. Case functions take no arguments, so when
you need to pass something along, wrap the call in a lambda. Writing
`s.case('b', process_with_data(val))` would call the function immediately and
register its *return value* as the action, which is not what you want.

## What you get

* **A shape that says "switch."** Value at the top, keys down the side, one
  action per key. It reads the way the idea sounds in your head.
* **Any hashable key.** Numbers, strings, `None`, enums, your own objects.
  Matching is plain equality, so `1`, `1.0` and `True` are the same key.
* **Many keys, one action.** Pass a list or a `range` and every item becomes a
  case for the same function.
* **A captured result.** Whatever the matched function returns is yours as
  `s.result` after the block.
* **Fall-through, strictly opt-in.** `fallthrough=True` on a case makes the next
  one run as well. Nothing falls through by accident.
* **Validation that fails loudly and early.** Duplicate keys, actions that are
  not callable, empty lists of keys, and a value that matches nothing with no
  default: all raise instead of silently doing the wrong thing.

## Many keys, one action

Lists and ranges expand into one case per item. Both of these route `4` to the
first case:

```python
value = 4

with switch(value) as s:
    s.case([0, 2, 4, 6, 8], lambda: 'even')
    s.case([1, 3, 5, 7], lambda: 'odd')
    s.default(lambda: 'out of range')

with switch(value) as s:
    s.case(range(1, 6), lambda: 'low')
    s.case(range(6, 10), lambda: 'high')
    s.default(lambda: 'out of range')
```

`case()` returns `True` if the key (or any item of a list or range key) matched,
in case you want to know at registration time.

## Closed vs. open ranges, or the fencepost problem

Look at the `range` example again. `6` appears at the end of one case and the
start of the next. It isn't a duplicate, because `range(1, 6)` stops at `5`, but
you have to *know* that to read the code. Half-open ranges are the right design
for slicing and loops. For "levels one through five" they make you do arithmetic.

So switchlang ships `closed_range(start, stop)`, inclusive on both ends:

```python
from switchlang import switch, closed_range

with switch(value) as s:
    s.case(closed_range(1, 5), lambda: 'one to five')   # 1, 2, 3, 4, 5
    s.case(closed_range(6, 9), lambda: 'six to nine')   # 6, 7, 8, 9
    s.default(lambda: 'something else')
```

A `step` is allowed and never overshoots: `closed_range(1, 6, 2)` is `1, 3, 5`,
and `closed_range(1, 7, 2)` is `1, 3, 5, 7` because the step lands on `7`.

One consequence of "inclusive on both ends": adjacent closed ranges share a
number. `closed_range(1, 5)` and `closed_range(5, 9)` both contain `5`, and
switchlang will refuse the second one with a duplicate-case error. Write
`closed_range(6, 9)` for the neighbor and the gap disappears.

## Fall-through, on purpose

In C, fall-through is the default, and "forgot the `break`" is a bug with its own
Wikipedia section. In switchlang it is the other way around. Cases stop after
themselves unless you ask:

```python
value = 2

with switch(value) as s:
    s.case(1, lambda: 'one')
    s.case(2, lambda: 'two', fallthrough=True)
    s.case(3, lambda: 'three')   # runs too; its key is never compared
    s.default(lambda: 'other')

print(s.result)   # 'three'
```

When `2` matches, its function is queued, and because it asked to fall through,
the *next registered case* is queued as well, whether or not `3` equals the
value. That case didn't ask to fall through, so the chain ends there. Chain as
many as you like; `result` is the return value of the last function that ran.

## The result

`s.result` is the return value of the matched case's function, read **after** the
block:

```python
with switch(status_code) as s:
    s.case(closed_range(200, 299), lambda: 'ok')
    s.case([301, 302, 307, 308], lambda: 'redirect')
    s.case(404, lambda: 'missing')
    s.default(lambda: 'error')

label = s.result
```

Read it *inside* the block and you get an exception, because nothing has run yet.
`None` is a perfectly good result (a function that returns nothing still counts
as having run) and is kept distinct from "nothing was computed."

## The house rules

A few things worth knowing before you build something on this.

* **Cases run on block exit, not on registration.** It bears repeating because
  every other behavior follows from it. `case()` and `default()` only register;
  `__exit__` does the work.
* **Register `default()` last.** It is implemented as an ordinary case keyed on a
  private sentinel, and ordering is not enforced. A default registered *before*
  a case that also matches will run alongside it. Put it at the bottom, where
  you'd expect it anyway.
* **Keys must be hashable.** They're stored in a set to catch duplicates.
* **No match and no default raises.** switchlang would rather tell you than
  quietly skip the block.
* **An exception inside the block aborts the switch.** If your registration code
  raises, the exception propagates and *no case action runs*. The queue is thrown
  away with the block.

## Why not just a `dict`?

The classic push-back: "we already have this." You build a dict of functions and
call `.get()`:

```python
switch = {
    1: method_on_one,
    2: method_on_two,
    3: method_three,
}

result = switch.get(value, default_method_to_run)()
```

For three integer keys, fine. Now give it the real menu from the story. Here it
is with switchlang:

```python
while True:
    action = get_action(action)

    with switch(action) as s:
        s.case(['c', 'a'], create_account)
        s.case('l', log_into_account)
        s.case('r', register_cage)
        s.case('u', update_availability)
        s.case(['v', 'b'], view_bookings)
        s.case('x', exit_app)
        s.case('', lambda: None)
        s.case(range(1, 6), lambda: set_level(action))
        s.default(unknown_command)

    print(f'Result is {s.result}')
```

And the same thing as a dict, the *pythonic* way:

```python
while True:
    action = get_action(action)

    switch = {
        'c': create_account,
        'a': create_account,
        'l': log_into_account,
        'r': register_cage,
        'u': update_availability,
        'v': view_bookings,
        'b': view_bookings,
        'x': exit_app,
        1: lambda: set_level(action),
        2: lambda: set_level(action),
        3: lambda: set_level(action),
        4: lambda: set_level(action),
        5: lambda: set_level(action),
        '': lambda: None,
    }
    result = switch.get(action, unknown_command)()
    print(f'Result is {result}')
```

Every shared action is written twice. The range is unrolled by hand. And if a
later edit adds a second `'a'` key, Python's dict literal will silently keep the
last one; no error, no warning, just a command that stopped working. switchlang
raises on the duplicate the first time the block runs.

I much prefer to read and write the first version. That's why this module
exists. Both are options, but one of them says what it means.

## Why not just `if / elif / else`?

The other classic push-back. A switch is "just" an if chain, so write the chain:

```python
while True:
    action = get_action(action)

    if action == 'c' or action == 'a':
        result = create_account()
    elif action == 'l':
        result = log_into_account()
    elif action == 'r':
        result = register_cage()
    elif action == 'a':
        result = update_availability()
    elif action == 'v' or action == 'b':
        result = view_bookings()
    elif action == 'x':
        result = exit_app()
    elif action in {1, 2, 3, 4, 5}:
        result = set_level(action)
    else:
        unknown_command()

    print(f'Result is {result}')
```

Honestly, I think this reads better than the dict. But take another look, because
that block has two bugs in it, and they are the kind that ship.

* **The `else` never sets `result`.** The `print` below will raise
  `NameError` (or print a stale value from the previous loop), but only when an
  unknown command comes in, which is exactly the branch nobody tests.
* **`update_availability` can never run.** Its letter is `'a'`, and `'a'` was
  already claimed by the `create_account` branch above it. The second check is
  dead code, and nothing in Python will tell you.

Now compare with the switchlang version from the previous section. It is the
same logic, but the duplicate key is a `ValueError` the first time the block
runs, the default always contributes a result, the shared keys are lists, and
the range is a range. If you ever want fall-through, it is one keyword away
instead of a restructuring.

## Why not just `match`?

Python 3.10 added structural pattern matching, and it is excellent at what it
was built for: taking data apart by *shape*. Tuples, dataclasses, nested
structures, sequences with wildcards. If that is your problem, use `match`.

But it covers different ground from a classic value switch:

* **No fall-through.** `match` arms are exclusive. switchlang's is opt-in per
  case.
* **Arms are syntax, not data.** You can't build `match` cases from a list at
  runtime. `s.case(some_list, action)` and `s.case(closed_range(1, 5), action)`
  are ordinary method calls, so you can.
* **The capture trap.** In a `case` pattern, a bare name like `case other:` does
  not compare against a variable named `other`; it *binds* a new one and matches
  everything. It is the most famous `match` gotcha, and it cannot happen here,
  because keys are values.
* **No result capture.** `match` arms are statement blocks. switchlang dispatches
  to callables and hands back the chosen one's return value.
* **Python version.** `match` needs 3.10+. switchlang runs on 3.9+.

Pattern-matching on structure: `match`. Explicit dispatch on values with ranges,
fall-through and a captured result: switchlang.

## How it works under the hood

There is no magic, and that's rather the point. `switch` is a class with
`__enter__` and `__exit__`. `__enter__` hands you the instance. Each `case()`
checks the key for duplicates, checks that the action is callable, compares the
key to the value with `==`, and if it matches, appends the function to a small
internal list. `default()` is `case()` with a private sentinel as the key.
`__exit__` first checks whether your block raised (if so, it re-raises and runs
nothing), then calls each queued function in order and stores the last return
value for `result`.

That is the whole mechanism. About 200 lines, readable in one sitting, with a
test suite pinning down every behavior described on this page.
