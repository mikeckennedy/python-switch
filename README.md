# python-switch

Adds switch blocks to Python.

This module adds explicit switch functionality to Python 
without changing the language. It builds upon a standard
way to define execution blocks: the `with` statement.

## Example

```python
from switchlang import switch

num = 7
val = input("Enter a key. a, b, c or any other: ")

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
    s.case(range(1, 5), lambda: ...)
    s.case(range(6, 7), lambda: ...)
    s.default(lambda: ...)
```

**Warning / open for debate**: 

I'm a little unsure what is the right way to handle this.
On one hand, reading `case(range(1,5))` seems like it should
include `1, 2, 3, 4, 5`. But `list(range(1,5))` is `[1,2,3,4]`. 
So that would be inconsistent.

Thoughts? I'm going with `1,2,3,4,5` for `range(1,5)` for now. 


