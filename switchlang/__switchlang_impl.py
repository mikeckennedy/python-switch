import uuid
from typing import Callable, Any, Optional


class switch:
    """
        switch is a module-level implementation of the switch statement for Python.
        See https://github.com/mikeckennedy/python-switch for full details.
        Copyright Michael Kennedy (https://twitter.com/mkennedy)
        License: MIT
    """
    __no_result = uuid.uuid4()
    __default = uuid.uuid4()

    def __init__(self, value):
        self.value = value
        self.cases = set()
        self._found = False
        self.__result = switch.__no_result
        self._falling_through = False
        self._func_stack = []

    def default(self, func: Callable[[], Any]):
        """
        Use as option final statement in switch block.

        ```
            with switch(val) as s:
               s.case(...)
               s.case(...)
               s.default(function)
        ```

        :param func: Any callable taking no parameters to be executed if this (default) case matches.
        :return: None
        """
        self.case(switch.__default, func)

    def case(self, key, func: Callable[[], Any], fallthrough: Optional[bool] = False):
        """
        Specify a case for the switch block:

        ```
            with switch(val) as s:
               s.case('a', function)
               s.case('b', function, fallthrough=True)
               s.default(function)
        ```

        :param key: Key for the case test (if this is a list or range, the items will each be added as a case)
        :param func: Any callable taking no parameters to be executed if this case matches.
        :param fallthrough: Optionally fall through to the subsequent case (defaults to False)
        :return:
        """
        if fallthrough is not None:
            if self._falling_through:
                self._func_stack.append(func)
                if not fallthrough:
                    self._falling_through = False

        if isinstance(key, range):
            key = list(key)

        if isinstance(key, list):
            if not key:
                raise ValueError("You cannot pass an empty collection as the case. It will never match.")

            found = False
            for i in key:
                if self.case(i, func, fallthrough=None):
                    found = True
                    if fallthrough is not None:
                        self._falling_through = fallthrough

            return found

        if key in self.cases:
            raise ValueError(f"Duplicate case: {key}")
        if not func:
            raise ValueError("Action for case cannot be None.")
        if not callable(func):
            raise ValueError("Func must be callable.")

        self.cases.add(key)
        if key == self.value or not self._found and key == self.__default:
            self._func_stack.append(func)
            self._found = True
            if fallthrough is not None:
                self._falling_through = fallthrough
            return True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            raise exc_val

        if not self._func_stack:
            raise Exception("Value does not match any case and there "
                            "is no default case: value {}".format(self.value))

        for func in self._func_stack:
            # noinspection PyCallingNonCallable
            self.__result = func()

    @property
    def result(self):
        """
        The value captured from the method called for a given case.

        ```
            value = 4
            with switch(value) as s:
                s.case(closed_range(1, 5), lambda: "1-to-5")
                # ...

            res = s.result  # res == '1-to-5'
        ```

        :return: The value captured from the method called for a given case.
        """
        if self.__result == switch.__no_result:
            raise Exception("No result has been computed (did you access "
                            "switch.result inside the with block?)")

        return self.__result


def closed_range(start: int, stop: int, step=1) -> range:
    """
    Creates a closed range that allows you to specify a case
    from [start, stop] inclusively.

    ```
        with switch(value) as s:
            s.case(closed_range(1, 5), lambda: "1-to-5")
            s.case(closed_range(6, 7), lambda: "6")
            s.default(lambda: 'default')
    ```

    :param start: The inclusive lower bound of the range [start, stop].
    :param stop: The inclusive upper bound of the range [start, stop].
    :param step: The step size between elements (defaults to 1).
    :return: A range() generator that has a closed upper bound.
    """
    if start >= stop:
        raise ValueError("Start must be less than stop.")

    return range(start, stop + step, step)
