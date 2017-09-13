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
* Could be extended for "fall-through" cases (doesn't yet)


