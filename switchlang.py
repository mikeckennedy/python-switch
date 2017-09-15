# Here is a first pass implementation at adding switch
import uuid
import collections.abc as abc
from typing import Callable, Any, Optional


class switch:
    """
    A context-manager acting as an implementation of a switch statement.
    """
    def __init__(self, value, fall_through=False):
        """
        Initialize switch context manager.

        Args:
            value: The value we dispatch on
            fall_through: If false, do not execute cases after the first case is matched

        i.e.

        meaning_of_life = 42
        with switch(42, fall_through=False) as s:
            s.case(42, lambda: print('hello, world') # this will execute
            s.case([42, 0], lambda: None) # this will NOT execute

        with switch(42, fall_through=True) as s:
            s.case(42, lambda: print('hello, world') # this will execute
            s.case([42, 0], lambda: None) # this WILL execute
        """
        self.value = value
        self.fall_through = fall_through
        self.called = False  # flag that determines if any pattern was matched prior to default

    def case(self, key, func: Callable[[], Any]) -> Optional[Any]:
        """
        Determine if the key matches self.value and return the result of the function if so.

        If match is found, set self.called to True and return func() else None

        Args:
            key: The values to dispatch on
            func: The function to call on self.value

        Returns: func() or None

        """
        # handle instances where a match has been found already and we don't want to fall through
        if not self.fall_through and self.called:
            return None

        if not callable(func):
            raise ValueError("Func must be callable.")

        if isinstance(key, abc.Mapping):
            raise ValueError('You cannot dispatch on a mapping')
        elif isinstance(key, abc.Iterable) and not isinstance(key, str):
            if self.value in key: # match on values
                self.called = True
                return func()
            else:  # match on predicates
                predicates = (f for f in key if callable(f))
                if any(p(self.value) for p in predicates):
                    self.called = True
                    return func()

        if key == self.value:  # check to see if the key matches self.value
            self.called = True
            return func()
        elif callable(key) and key(self.value):  # the key is a predicate function
            self.called = True
            return func()

    def default(self, func: Callable[[], Any]) -> None:
        """
        Set the default function to be called if argument not matched.
        Args:
            func: Callable

        Returns: None

        """
        if not self.fall_through and self.called:
            return None

        self.called = True
        return func()


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            raise exc_val
        elif not self.called:
            raise Exception("Value does not match any case and there "
                            "is no default case: value {}".format(self.value))
