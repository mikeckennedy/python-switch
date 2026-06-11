## closed_range()


Create a closed range for a case: both `start` and `stop` are included.


Usage

``` python
closed_range(
    start,
    stop,
    step=1,
)
```


With the default step of 1, `closed_range(1, 5)` covers 1, 2, 3, 4, 5 -- unlike `range(1, 5)`, the upper bound is part of the range.

        with switch(value) as s:
            s.case(closed_range(1, 5), lambda: "1-to-5")
            s.case(closed_range(6, 7), lambda: "6-or-7")
            s.default(lambda: 'default')


## Parameters


`start: int`  
The inclusive lower bound of the range.

`stop: int`  
The inclusive upper bound of the range.

`step: int = ``1`  
The step size between elements (defaults to 1).


## Returns


`range`  
A range object with a closed (inclusive) upper bound.


## Raises


`ValueError`  
If start is not less than stop.
