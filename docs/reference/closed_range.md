## closed_range()


Creates a closed range that allows you to specify a case


Usage

``` python
closed_range(
    start,
    stop,
    step=1,
)
```


from \[start, stop\] inclusively.

        with switch(value) as s:
            s.case(closed_range(1, 5), lambda: "1-to-5")
            s.case(closed_range(6, 7), lambda: "6")
            s.default(lambda: 'default')


## Parameters


`start: int`  
The inclusive lower bound of the range \[start, stop\].

`stop: int`  
The inclusive upper bound of the range \[start, stop\].

`step=``1`  
The step size between elements (defaults to 1).


## Returns


`range`  
A range() generator that has a closed upper bound.
