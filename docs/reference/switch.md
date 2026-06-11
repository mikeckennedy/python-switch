## switch


switch is a module-level implementation of the switch statement for Python.


Usage

``` python
switch()
```


See https://github.com/mikeckennedy/python-switch for full details. Copyright Michael Kennedy (https://mkennedy.codes) License: MIT


## Attributes

| Name | Description |
|----|----|
| [result](#result) | The value captured from the method called for a given case. |

------------------------------------------------------------------------


#### result


The value captured from the method called for a given case.


`result`


        value = 4
        with switch(value) as s:
            s.case(closed_range(1, 5), lambda: "1-to-5")
            # ...

        res = s.result  # res == '1-to-5'


## Methods

| Name | Description |
|----|----|
| [__enter__()](#__enter__) | Enter the switch block. |
| [__exit__()](#__exit__) | Run the matched case (and any fall-through cases) as the block exits. |
| [__init__()](#__init__) | Create a new switch block that tests cases against `value`. |
| [case()](#case) | Specify a case for the switch block: |
| [default()](#default) | Use as option final statement in switch block. |

------------------------------------------------------------------------


#### \_\_enter\_\_()


Enter the switch block.


Usage

``` python
__enter__()
```


##### Returns


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


`value: typing.Any`  
The value each case key is compared against.


------------------------------------------------------------------------


#### case()


Specify a case for the switch block:


Usage

``` python
case(key, func, fallthrough=False)
```


        with switch(val) as s:
           s.case('a', function)
           s.case('b', function, fallthrough=True)
           s.default(function)


##### Parameters


`key: typing.Any`  
Key for the case test (if this is a list or range, the items will each be added as a case)

`func: typing.Callable[[], typing.Any]`  
Any callable taking no parameters to be executed if this case matches.

`fallthrough: typing.Optional[bool] = ``False`  
Optionally fall through to the subsequent case (defaults to False)


##### Returns


True if this case matched the switch value, otherwise None.


------------------------------------------------------------------------


#### default()


Use as option final statement in switch block.


Usage

``` python
default(func)
```


        with switch(val) as s:
           s.case(...)
           s.case(...)
           s.default(function)


##### Parameters


`func: typing.Callable[[], typing.Any]`  
Any callable taking no parameters to be executed if this (default) case matches.


##### Returns


None
