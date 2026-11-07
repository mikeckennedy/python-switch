# Patterns

A few shapes that come up again and again once a switch block is available. Each example runs as shown.


# Wrap the block in a function

Most switch blocks exist to produce a value, and a function that returns `s.result` is the cleanest way to use one. It gives the switch a name, keeps `s` out of the enclosing scope, and makes the result available where the caller wants it:


``` python
from switchlang import switch, closed_range


def shipping_cost(weight_kg):
    with switch(weight_kg) as s:
        s.case(closed_range(0, 1), lambda: 5.00)
        s.case(closed_range(2, 5), lambda: 9.50)
        s.case(closed_range(6, 20), lambda: 19.00)
        s.default(lambda: 'quote required')
    return s.result


print(shipping_cost(1), shipping_cost(4), shipping_cost(12), shipping_cost(80))
```


    5.0 9.5 19.0 quote required


# A command loop

The example that motivated the library: a loop that reads a command and dispatches on it. The input is scripted here so the page can run, but the shape is the same with `input()`:


``` python
inputs = iter(['a', '3', 'v', 'q'])


def get_action():
    return next(inputs)


state = {'level': None, 'running': True}


def set_level(n):
    state['level'] = n
    return f'level set to {n}'


def quit_app():
    state['running'] = False
    return 'bye'


while state['running']:
    action = get_action()

    with switch(action) as s:
        s.case(['a', 'c'], lambda: 'create account')
        s.case(['v', 'b'], lambda: 'view bookings')
        s.case([str(n) for n in range(1, 6)], lambda: set_level(int(action)))
        s.case('q', quit_app)
        s.case('', lambda: None)
        s.default(lambda: f'unknown command {action!r}')

    print(f'{action!r} -> {s.result}')
```


    'a' -> create account
    '3' -> level set to 3
    'v' -> view bookings
    'q' -> bye


Two things to notice. The lambdas close over `action`, so the digit case can read the value that matched. And the digit keys are built with a list comprehension: a case key is an ordinary expression, so it can come from anywhere.


# Cases built from data

Because [case()](../reference/switch.md#switchlang.switch.case) is a method call, you can register cases in a loop. That makes a switch block a good front end for a table of handlers that lives in configuration or is assembled at startup:


``` python
parsers = {
    'json': lambda: 'parse as JSON',
    'yaml': lambda: 'parse as YAML',
    'toml': lambda: 'parse as TOML',
}

extension = 'yaml'

with switch(extension) as s:
    for key, handler in parsers.items():
        s.case(key, handler)
    s.default(lambda: f'no parser for .{extension}')

print(s.result)
```


    parse as YAML


You still get duplicate detection and the "nothing matched" check, which a bare dict lookup doesn't give you. If the table is the whole story and never changes, a dict is fine on its own; the switch earns its keep when some cases are data and others are code.


# A state machine on tuple keys

Tuples are hashable, so a `(state, event)` pair is a valid key. That turns a transition table into a switch block, with [default()](../reference/switch.md#switchlang.switch.default) as "stay where you are":


``` python
from enum import Enum, auto


class Job(Enum):
    QUEUED = auto()
    RUNNING = auto()
    DONE = auto()
    FAILED = auto()


def next_state(state, event):
    with switch((state, event)) as s:
        s.case((Job.QUEUED, 'start'), lambda: Job.RUNNING)
        s.case((Job.RUNNING, 'finish'), lambda: Job.DONE)
        s.case((Job.RUNNING, 'error'), lambda: Job.FAILED)
        s.case((Job.FAILED, 'retry'), lambda: Job.QUEUED)
        s.default(lambda: state)
    return s.result


job = Job.QUEUED
for event in ['start', 'error', 'retry', 'start', 'finish', 'start']:
    job = next_state(job, event)
    print(f'{event:7} -> {job.name}')
```


    start   -> RUNNING
    error   -> FAILED
    retry   -> QUEUED
    start   -> RUNNING
    finish  -> DONE
    start   -> DONE


The last `'start'` arrives in `DONE`, where it means nothing, and the default keeps the job where it is.


# An explicit "do nothing" case

Sometimes a value is valid and should do nothing, and you want that written down rather than left to the default. `lambda: None` is the idiom:

``` python
s.case('', lambda: None)   # empty input: ignore it
```

It reads as a decision, which is the point. The default stays free to mean "this value was not expected."


# Grouped actions with fall-through

Fall-through is rare in practice, and when you want it, it is usually to share a tail of work between neighboring cases. Here the "verbose" level does everything "normal" does, plus more:


``` python
def configure_logging(level):
    steps = []
    with switch(level) as s:
        s.case('verbose', lambda: steps.append('log every request'), fallthrough=True)
        s.case('normal', lambda: steps.append('log errors and warnings'), fallthrough=True)
        s.case('quiet', lambda: steps.append('log errors only'))
        s.default(lambda: steps.append('unknown level, logging errors only'))
    return steps


print(configure_logging('verbose'))
print(configure_logging('quiet'))
```


    ['log every request', 'log errors and warnings', 'log errors only']
    ['log errors only']


The order of the cases is the order of the chain, so arrange them from "most" to "least". [Fall-through](fall-through.md) explains the rules.
