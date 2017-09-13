import unittest
from switchlang import switch


# here is a custom type we can use as a key for our tests
class TestKeyObject:
    pass


class CoreTests(unittest.TestCase):
    def test_has_matched_case_int(self):
        value = 7

        executed_case = None

        def get_set_case(val):
            nonlocal executed_case
            executed_case = val

        with switch(value) as s:
            s.case(1, lambda: get_set_case("one"))
            s.case(5, lambda: get_set_case("five"))
            s.case(7, lambda: get_set_case("seven"))
            s.default(lambda: get_set_case('default'))

        self.assertEqual(executed_case, "seven")

    def test_has_matched_case_object(self):
        t1 = TestKeyObject()
        t2 = TestKeyObject()
        t3 = TestKeyObject()
        value = t2

        executed_case = None

        def get_set_case(val):
            nonlocal executed_case
            executed_case = val

        with switch(value) as s:
            s.case(t1, lambda: get_set_case(t1))
            s.case(t2, lambda: get_set_case(t2))
            s.case(t3, lambda: get_set_case(t3))
            s.default(lambda: get_set_case(None))

        self.assertEqual(executed_case, t2)

    def test_default_passthrough(self):
        value = 11
        executed_case = None

        def get_set_case(val):
            nonlocal executed_case
            executed_case = val

        with switch(value) as s:
            s.case(1, lambda: get_set_case(1))
            s.case(2, lambda: get_set_case(2))
            s.default(lambda: get_set_case("default"))

        self.assertEqual(executed_case, "default")

    def test_none_as_valid_case(self):
        value = None
        executed_case = None

        def get_set_case(val):
            nonlocal executed_case
            executed_case = val

        with switch(value) as s:
            s.case(1, lambda: get_set_case(1))
            s.case(None, lambda: get_set_case(None))
            s.default(lambda: get_set_case("default"))

        self.assertEqual(executed_case, None)

    def test_error_no_match_no_default(self):
        with self.assertRaises(Exception):
            with switch('val') as s:
                s.case(1, lambda: None)
                s.case(1, lambda: None)

    def test_error_duplicate_case(self):
        with self.assertRaises(ValueError):
            with switch('val') as s:
                s.case(1, lambda: None)
                s.case(1, lambda: None)
