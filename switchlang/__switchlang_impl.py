from __future__ import annotations

import uuid
from collections.abc import Callable
from types import TracebackType
from typing import Any


class switch:
    """
    An explicit switch statement for Python, implemented as a context manager.

    Use it in a `with` block: register cases with `case()` and `default()`,
    then read the matched case's return value from `result`.

    See https://github.com/mikeckennedy/python-switch for full details.
    Copyright Michael Kennedy (https://mkennedy.codes)
    License: MIT
    """

    __no_result: Any = uuid.uuid4()
    __default: Any = uuid.uuid4()

    def __init__(self, value: Any) -> None:
        """
        Create a new switch block that tests cases against `value`.

        :param value: The value each case key is compared against.
        """
        self.value = value
        self.cases: set[Any] = set()
        self._found = False
        self.__result = switch.__no_result
        self._falling_through = False
        self._func_stack: list[Callable[[], Any]] = []

    def default(self, func: Callable[[], Any]) -> None:
        """
        Register the default case: the action to run when no other case matches.

        Use it as the optional final statement in the switch block. Note that
        the ordering is not enforced: if `default()` is registered before a case
        that also matches, both will run. Always register it last.

        ```
            with switch(val) as s:
               s.case(...)
               s.case(...)
               s.default(function)
        ```

        :param func: Any callable taking no parameters, executed if no other case matched.
        :return: None
        """
        self.case(switch.__default, func)

    def case(
        self,
        key: Any,
        func: Callable[[], Any],
        fallthrough: bool | None = False,
    ) -> bool:
        """
        Register a case for the switch block:

        ```
            with switch(val) as s:
               s.case('a', function)
               s.case('b', function, fallthrough=True)
               s.default(function)
        ```

        :param key: Key for the case test. If this is a list or range, each item is added as a case for `func`.
        :param func: Any callable taking no parameters, executed if this case matches.
        :param fallthrough: Optionally fall through to the subsequent case (defaults to False).
                            `None` is reserved for internal use and leaves the fall-through state unchanged.
        :return: True if this case (or any item of a list or range key) matched the switch value, otherwise False.
        :raises ValueError: If the key is a duplicate, the key is an empty collection, or func is not callable.
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
                raise ValueError('You cannot pass an empty collection as the case. It will never match.')

            found = False
            for i in key:
                if self.case(i, func, fallthrough=None):
                    found = True
                    if fallthrough is not None:
                        self._falling_through = fallthrough

            return found

        if key in self.cases:
            raise ValueError(f'Duplicate case: {key}')
        if func is None:
            raise ValueError('Action for case cannot be None.')
        if not callable(func):
            raise ValueError('Func must be callable.')

        self.cases.add(key)
        if key == self.value or not self._found and key == self.__default:
            self._func_stack.append(func)
            self._found = True
            if fallthrough is not None:
                self._falling_through = fallthrough
            return True

        return False

    def __enter__(self) -> switch:
        """
        Enter the switch block.

        :return: The switch instance itself (bind it with `as s` to register cases).
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Run the matched case (and any fall-through cases) as the block exits.

        :raises Exception: If no case matched the value and no default case was registered.
        """
        # Test for the presence of an exception, not its truthiness: an exception
        # whose __bool__/__len__ is falsy must still abort the switch (see #15).
        if exc_val is not None:
            raise exc_val

        if not self._func_stack:
            raise Exception(f'Value does not match any case and there is no default case: value {self.value}')

        for func in self._func_stack:
            # noinspection PyCallingNonCallable
            self.__result = func()

    @property
    def result(self) -> Any:
        """
        The value returned by the function of the matched case.

        When cases fall through, `result` is the return value of the last
        function executed.

        ```
            value = 4
            with switch(value) as s:
                s.case(closed_range(1, 5), lambda: "1-to-5")
                # ...

            res = s.result  # res == '1-to-5'
        ```

        :return: The value returned by the matched case's function (the last one executed when falling through).
        :raises Exception: If accessed before the switch block has exited and computed a result.
        """
        # Identity, not equality: a result with a permissive __eq__ (e.g. a numpy
        # array) must not be mistaken for the no-result sentinel.
        if self.__result is switch.__no_result:
            raise Exception('No result has been computed (did you access switch.result inside the with block?)')

        return self.__result


def closed_range(start: int, stop: int, step: int = 1) -> range:
    """
    Create a closed range for a case: both `start` and `stop` are included.

    With the default step of 1, `closed_range(1, 5)` covers 1, 2, 3, 4, 5 —
    unlike `range(1, 5)`, the upper bound is part of the range. With a larger
    step the range never goes past `stop`: `closed_range(1, 6, 2)` covers
    1, 3, 5, and `stop` itself is included when the step lands on it exactly,
    as in `closed_range(1, 7, 2)` -> 1, 3, 5, 7.

    ```
        with switch(value) as s:
            s.case(closed_range(1, 5), lambda: "1-to-5")
            s.case(closed_range(6, 7), lambda: "6-or-7")
            s.default(lambda: 'default')
    ```

    :param start: The inclusive lower bound of the range.
    :param stop: The inclusive upper bound of the range.
    :param step: The step size between elements; must be 1 or greater (defaults to 1).
    :return: A range object with a closed (inclusive) upper bound.
    :raises ValueError: If start is not less than stop, or step is less than 1.
    """
    if start >= stop:
        raise ValueError('Start must be less than stop.')
    if step < 1:
        raise ValueError('Step must be 1 or greater.')

    return range(start, stop + 1, step)
