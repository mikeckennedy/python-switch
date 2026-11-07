# Getting started

This page installs switchlang, writes a first switch block, and explains the one idea you need in order to use it well: the cases run when the block *ends*, not when you write them.


# Install

``` bash
pip install switchlang
# or
uv add switchlang
```

switchlang supports Python 3.9 and newer. It is about 200 lines of code with no runtime dependencies, and it ships type hints (a `py.typed` marker), so your editor and type checker know what `s.case` and `s.result` are.


# Your first switch


``` python
from switchlang import switch


def greet():
    return 'Hello!'


def farewell():
    return 'Goodbye!'


def shrug():
    return 'Not sure what you meant.'


command = 'hi'

with switch(command) as s:
    s.case('hi', greet)
    s.case('bye', farewell)
    s.default(shrug)

print(s.result)
```


    Hello!


Reading top to bottom:

- `switch(command)` opens the block and remembers the value to test.
- Each `s.case(key, func)` *registers* a case. The key is compared to the value with `==`. `func` is stored, not called.
- `s.default(func)` registers what to run when nothing else matched. Make it the last line of the block.
- When the block ends, the matched function runs. Its return value is then available as `s.result`.

That last point is the whole design. A `with` statement has a well-defined end, and switchlang uses that moment to execute whatever matched. [How a switch block runs](how-it-works.md) goes through it step by step.


# Pass arguments with a lambda

Case functions take no arguments. When the action needs some, wrap the call in a lambda:


``` python
def set_volume(level):
    return f'volume set to {level}'


level = 7

with switch('v') as s:
    s.case('v', lambda: set_volume(level))
    s.case('m', lambda: set_volume(0))
    s.default(lambda: 'unknown command')

print(s.result)
```


    volume set to 7


Without the lambda, `s.case('v', set_volume(level))` would call `set_volume` immediately and hand its return value, a string, to [case()](../reference/switch.md#switchlang.switch.case) as the action. switchlang refuses that at once rather than failing later:


``` python
try:
    with switch('v') as s:
        s.case('v', set_volume(level))
except ValueError as e:
    print(e)
```


    Func must be callable.


# Several keys, one action

A list or a range as the key registers one case per item, all pointing at the same function. [closed_range](../reference/closed_range.md#switchlang.closed_range) is a range that includes both ends:


``` python
from switchlang import closed_range


def grade(score):
    with switch(score) as s:
        s.case(closed_range(90, 100), lambda: 'A')
        s.case(closed_range(80, 89), lambda: 'B')
        s.case(closed_range(70, 79), lambda: 'C')
        s.default(lambda: 'needs work')
    return s.result


print([grade(n) for n in (95, 83, 71, 40)])
```


    ['A', 'B', 'C', 'needs work']


Wrapping the block in a function that returns `s.result`, as `grade()` does, is the most common way to use switchlang. [Keys and matching](keys-and-matching.md) covers lists, ranges and what makes a valid key.


# Next steps

- [How a switch block runs](how-it-works.md): the execution model, and what happens when something goes wrong inside the block.
- [Fall-through](fall-through.md): run the next case too, on purpose.
- [Results](results.md): everything about `s.result`.
- [Errors and validation](errors.md): what switchlang refuses, and when.
- [Patterns](patterns.md): command loops, dispatch tables built from data, state machines.
- [switch, dict, if/elif or match?](alternatives.md): when to reach for which.
