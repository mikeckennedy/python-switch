# python-switch

Adds switch blocks to Python.

This module adds explicit switch functionality to Python 
without changing the language. It builds upon a standard
way to define execution blocks: the `with` statement.

## Example

```python
from switchlang import switch


def process_a():
    return "found a"


def process_any():
    return "found default"


def process_with_data(*value):
    return "found with data"


num = 7
val = 'b'

with switch(val) as s:
    a = s.case('a', process_a)  # -> None
    b = s.case('b', lambda: process_with_data(val, num, 'other values still'))  # -> "found with data"
    c = s.default(process_any)  # -> None


with switch(val, fall_through=True) as s:
    a = s.case('a', process_a)  # -> None
    b = s.case('b', lambda: process_with_data(val, num, 'other values still'))  # -> "found with data"

    c = s.case(lambda val: isinstance(val, str), lambda: "matched on predicate")  # -> "matched on predicate"

    d = s.default(process_any)  # -> "found default"
``` 

## Features

* More explicit than using dictionaries with functions as values.
* Verifies the signatures of the methods
* Supports default case
* Could be extended for "fall-through" cases (doesn't yet)
* Able to dispatch based on predicate functions as well as values

## Multiple cases, one action

You can map ranges and lists of cases to a single action as follows:

```python
# with lists:
value = 4  # matches even number case

with switch(value) as s:
    s.case([1, 3, 5, 7], lambda: ...)
    s.case([0, 2, 4, 6, 8], lambda: ...)
    s.default(lambda: ...)
``` 

## Why not just raw `dict`?

The biggest push back on this idea is that we already have this problem solved.
You write the following code.

```python
switch = {
    1: method_on_one,
    2: method_on_two,
    3: method_three
}

result = switch.get(value, defult_method_to_run)()
```

This works but is very low on the functionality level. We have a better solution here 
I believe. Let's take this example and see how it looks in python-switch vs raw dicts:

```python
# with python-switch:

while True:
    action = get_action(action)

    with switch(action) as s:
        
        cases = (
            s.case(['c', 'a'], create_account)
            s.case('l', log_into_account)
            s.case('r', register_cage)
            s.case('u', update_availability)
            s.case(['v', 'b'], view_bookings)
            s.case('x', exit_app)
            s.case('', lambda: None)
            s.case(range(1,6), lambda: set_level(action))
            s.default(unknown_command)
        )
        
        if any(cases):
            result, *_ = (case for case in cases if case)
        else:
            result = None
    
```

Now compare that to they espoused *pythonic* way:

```python
# with raw dicts

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
```

Personally, I much prefer to read and write the one above. That's why I wrote this module.
It seems to convey the intent of switch way more than the dict. But either are options.
