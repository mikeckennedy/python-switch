# How a switch block runs

switchlang adds no syntax to Python. [switch](../reference/switch.md#switchlang.switch) is a class with [__enter__](../reference/switch.md#switchlang.switch.__enter__) and [__exit__](../reference/switch.md#switchlang.switch.__exit__), so a switch block is an ordinary `with` statement. This page follows one from the `with` line to the line after it, because once the order of events is clear, every other behavior in this guide follows from it.


# Register first, run at the end

Here is a block that announces each step:


``` python
from switchlang import switch


def action():
    print('  3. the matched action runs')
    return 'done'


print('1. before the block')

with switch('a') as s:
    print('  2. registering cases')
    s.case('a', action)
    s.case('b', lambda: 'never called')
    print('  2. end of the block body')

print('4. after the block, result =', s.result)
```


    1. before the block
      2. registering cases
      2. end of the block body
      3. the matched action runs
    4. after the block, result = done


The action prints *after* the last line of the block body. Nothing about `s.case('a', action)` ran `action`; it only noted that `'a'` matched and queued the function. When the block closed, [__exit__](../reference/switch.md#switchlang.switch.__exit__) ran the queue.

In detail:

1.  `switch(value)` creates the instance and stores `value`.
2.  [__enter__](../reference/switch.md#switchlang.switch.__enter__) returns the instance, which `as s` binds.
3.  Each `s.case(key, func)` checks `key` for duplicates, checks that `func` is callable, compares `key == value`, and if they match appends `func` to an internal list. [default()](../reference/switch.md#switchlang.switch.default) is [case()](../reference/switch.md#switchlang.switch.case) with a private sentinel as the key.
4.  [__exit__](../reference/switch.md#switchlang.switch.__exit__) calls every queued function in order and keeps the last return value. Then `s.result` works.

Because the functions run at step 4, anything they depend on must be ready by the end of the block, and anything you do inside the block (logging, say) happens before any action.


# Why a `with` block?

Python offers few ways to run code "at the end of this group of statements" without new syntax. Decorators wrap a function, not a block. A `with` statement is exactly that hook: a clear start, a clear end, and a body in between. It also gives the block a visual shape, a value at the top and an indented list of cases below, which is the shape a switch statement has in every language that has one.


# [result](../reference/switch.md#switchlang.switch.result) inside the block

Reading `s.result` before the block ends raises, because nothing has run yet:


``` python
try:
    with switch('a') as s:
        s.case('a', lambda: 'x')
        print(s.result)
except Exception as e:
    print(type(e).__name__, '-', e)
```


    Exception - No result has been computed (did you access switch.result inside the with block?)


If you need to act on the outcome, do it on the line after the block, or wrap the block in a function that returns `s.result`.


# What [case()](../reference/switch.md#switchlang.switch.case) returns

[case()](../reference/switch.md#switchlang.switch.case) returns `True` when its key (or any item of a list or range key) matched the value. You rarely need it, but it is there:


``` python
with switch(3) as s:
    hit = s.case(3, lambda: 'three')
    miss = s.case(4, lambda: 'four')

print(hit, miss)
```


    True False


# When the block raises

If your own code raises inside the block, the exception propagates and the switch is abandoned. No queued action runs:


``` python
ran = []

try:
    with switch('a') as s:
        s.case('a', lambda: ran.append('a'))
        raise RuntimeError('something went wrong while registering')
except RuntimeError as e:
    print('propagated:', e)

print('actions that ran:', ran)
```


    propagated: something went wrong while registering
    actions that ran: []


[__exit__](../reference/switch.md#switchlang.switch.__exit__) checks for an in-flight exception before it touches the queue. The check is `exc_val is not None`, an identity test, so even an exception object that is falsy (one with a `__bool__` or `__len__` returning false) aborts the switch. That detail was a real bug once ([\#15](https://github.com/mikeckennedy/python-switch/issues/15)), and the test suite pins it.


# Next

- [Keys and matching](keys-and-matching.md): what can be a key, and how lists and ranges expand.
- [Errors and validation](errors.md): which mistakes are caught at registration and which at exit.
