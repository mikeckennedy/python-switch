# switchlang
[![](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/) 
[![](https://img.shields.io/pypi/l/markdown-subtemplate.svg)](https://github.com/mikeckennedy/python-switch/blob/master/LICENSE)
[![](https://img.shields.io/pypi/dm/python-switch.svg)](https://test.pypi.org/project/switchlang/)


Adds switch blocks to the Python language.

This module adds explicit switch functionality to Python 
without changing the language. It builds upon a standard
way to define execution blocks: the `with` statement.

## Example

```python
from switchlang import switch

num = 7
val = input("Enter a character, a, b, c or any other: ")

with switch(val) as s:
    s.case('a', process_a)
    s.case('b', lambda: process_with_data(val, num, 'other values still'))
    s.default(process_any)
    
def process_a():
    print("Found A!")
    
def process_any():
    print("Found Default!")
    
def process_with_data(*value):
    print("Found with data: {}".format(value))
``` 

## Installation

Simply install via pip:

```bash
pip install switchlang
```

## Features

* More explicit than using dictionaries with functions as values.
* Verifies the signatures of the methods
* Supports default case
* Checks for duplicate keys / cases
* Keys can be anything hashable (numbers, strings, objects, etc.)
* Could be extended for "fall-through" cases (doesn't yet)
* Use range and list for multiple cases mapped to a single action

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

```python
# with ranges:
value = 4  # matches first case

with switch(value) as s:
    s.case(range(1, 6), lambda: ...)
    s.case(range(6, 10), lambda: ...)
    s.default(lambda: ...)
```

## Closed vs. Open ranges

Looking at the above code it's a bit weird that 6 appears 
at the end of one case, beginning of the next. But `range()` is
half open/closed. 

To handle the inclusive case, I've added `closed_range(start, stop)`.
For example, `closed_range(1,5)` -> `[1,2,3,4,5]` 

## Why not just raw `dict`?

The biggest push back on this idea is that we already have this problem solved.
You write the following code.

```python
switch = {
    1: method_on_one,
    2: method_on_two,
    3: method_three
}

result = switch.get(value, default_method_to_run)()
```

This works but is very low on the functionality level. We have a better solution here 
I believe. Let's take this example and see how it looks in python-switch vs raw dicts:

```python
# with python-switch:

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
        s.case(range(1,6), lambda: set_level(action))
        s.default(unknown_command)
    
    print('Result is {}'.format(s.result))
```

Now compare that to the espoused *pythonic* way:

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
    print('Result is {}'.format(result))
```

Personally, I much prefer to read and write the one above. That's why I wrote this module.
It seems to convey the intent of switch way more than the dict. But either are options.

## Why not just `if / elif / else`?

The another push back on this idea is that we already have this problem solved.
Switch statements are really if / elif / else blocks. So you write the following code.

```python
# with if / elif / else

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
        
    print('Result is {}'.format(result))
```

I actually believe this is a little better than the 
[raw dict option](https://github.com/mikeckennedy/python-switch#why-not-just-raw-dict).
But there are still things that are harder. 

* How would you deal with fall-through cleanly?
* Did you notice the bug? We forgot to set result in default case (`else`) and will result in a runtime error (but only if that case hits).
* There is another bug. Update `update_availability` will never run because it's command (`a`) is bound to two cases. 
This is guarded against in switch and you would receive a duplicate case error the first time it runs at all.
* While it's pretty clear, it's much more verbose and less declarative than the switch version. 

Again, compare the if / elif / else to what you have with switch. This code is identical except 
doesn't have the default case bug.

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
        s.case(range(1,6), lambda: set_level(action))
        s.default(unknown_command)
    
    print('Result is {}'.format(s.result))
```
