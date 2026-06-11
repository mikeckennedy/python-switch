## switch


An explicit switch statement for Python, implemented as a context manager.


Usage

``` python
switch()
```


Use it in a `with` block: register cases with [case()](switch.md#switchlang.switch.case) and [default()](switch.md#switchlang.switch.default), then read the matched case's return value from [result](switch.md#switchlang.switch.result).

See https://github.com/mikeckennedy/python-switch for full details. Copyright Michael Kennedy (https://mkennedy.codes) License: MIT


## Attributes

| Name | Description |
|----|----|
| [result](#result) | The value returned by the function of the matched case. |

------------------------------------------------------------------------


#### result


The value returned by the function of the matched case.


`result: Any`


When cases fall through, [result](switch.md#switchlang.switch.result) is the return value of the last function executed.

        value = 4
        with switch(value) as s:
            s.case(closed_range(1, 5), lambda: "1-to-5")
            # ...

        res = s.result  # res == '1-to-5'


##### Raises


`Exception`  
If accessed before the switch block has exited and computed a result.


## Methods

| Name | Description |
|----|----|
| [__enter__()](#__enter__) | Enter the switch block. |
| [__exit__()](#__exit__) | Run the matched case (and any fall-through cases) as the block exits. |
| [__init__()](#__init__) | Create a new switch block that tests cases against `value`. |
| [case()](#case) | Register a case for the switch block: |
| [default()](#default) | Register the default case: the action to run when no other case matches. |

------------------------------------------------------------------------


#### \_\_enter\_\_()


Enter the switch block.


Usage

``` python
__enter__()
```


##### Returns


`switch`  
The switch instance itself (bind it with `as s` to register cases).


------------------------------------------------------------------------


#### \_\_exit\_\_()


Run the matched case (and any fall-through cases) as the block exits.


Usage

``` python
__exit__(exc_type, exc_val, exc_tb)
```


##### Raises


`Exception`  
If no case matched the value and no default case was registered.


------------------------------------------------------------------------


#### \_\_init\_\_()


Create a new switch block that tests cases against `value`.


Usage

``` python
__init__(value)
```


##### Parameters


`value: Any`  
The value each case key is compared against.


------------------------------------------------------------------------


#### case()


Register a case for the switch block:


Usage

``` python
case(key, func, fallthrough=False)
```


        with switch(val) as s:
           s.case('a', function)
           s.case('b', function, fallthrough=True)
           s.default(function)


##### Parameters


`key: Any`  
Key for the case test. If this is a list or range, each item is added as a case for `func`.

`func: Callable[[], Any]`  
Any callable taking no parameters, executed if this case matches.

`fallthrough: bool | None = ``False`  
Optionally fall through to the subsequent case (defaults to False). `None` is reserved for internal use and leaves the fall-through state unchanged.


##### Returns


`bool`  
True if this case (or any item of a list or range key) matched the switch value, otherwise False.


##### Raises


`ValueError`  
If the key is a duplicate, the key is an empty collection, or func is not callable.


------------------------------------------------------------------------


#### default()


Register the default case: the action to run when no other case matches.


Usage

``` python
default(func)
```


Use it as the optional final statement in the switch block. Note that the ordering is not enforced: if [default()](switch.md#switchlang.switch.default) is registered before a case that also matches, both will run. Always register it last.

        with switch(val) as s:
           s.case(...)
           s.case(...)
           s.default(function)


##### Parameters


`func: Callable[[], Any]`  
Any callable taking no parameters, executed if no other case matched.


##### Returns


`None`  
None
