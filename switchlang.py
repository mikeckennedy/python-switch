# Here is a first pass implementation at adding switch
from typing import Callable, Any


class switch:
    def __init__(self, value):
        self.value = value
        self.cases = {}

    def default(self, func: Callable[[], Any]):
        self.case('__default__', func)

    def case(self, key, func: Callable[[], Any]):
        if isinstance(key, range):
            for n in range(key.start, key.stop + 1, key.step):
                self.case(n, func)
            return

        if isinstance(key, list):
            for i in key:
                self.case(i, func)
            return

        if key in self.cases:
            raise ValueError("Duplicate case: {}".format(key))
        if not func:
            raise ValueError("Action for case cannot be None.")
        if not callable(func):
            raise ValueError("Func must be callable.")

        self.cases[key] = func

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            raise exc_val

        func = self.cases.get(self.value)
        if not func:
            func = self.cases.get('__default__')

        if not func:
            raise Exception("Value does not match any case and there is no default case: value {}".format(self.value))

        func()
