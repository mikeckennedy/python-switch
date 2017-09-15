import unittest
from switchlang import switch


# here is a custom type we can use as a key for our tests
class TestKeyObject:
    pass


class CoreTests(unittest.TestCase):
    def test_has_matched_value_no_fallthrough(self):
        value = 7
        with switch(value) as s:
            a = s.case(7, lambda: "seven")
            b = s.case(5, lambda: "five")
            c = s.default(lambda: 'default')

        self.assertEqual(a, "seven")
        self.assertEqual(b, None)
        self.assertEqual(c, None)

    def test_has_matched_value_fallthrough(self):
        value = 7
        with switch(value, fall_through=True) as s:
            a = s.case(7, lambda: "seven")
            b = s.case(5, lambda: "five")
            c = s.case((7, 81), lambda: "matched")
            d = s.default(lambda: 'default')

        self.assertEqual(a, "seven")
        self.assertEqual(b, None)
        self.assertEqual(c, "matched")
        self.assertEqual(d, "default")

    def test_match_on_predicate(self):
        value = 7
        with switch(value, fall_through=True) as s:
            a = s.case(lambda n: n < 10, lambda: "less than 10")
            b = s.case(lambda n: isinstance(n, int), lambda: "is integer")
            c = s.case(lambda n: False, lambda: "False")

        self.assertEqual(a, "less than 10")
        self.assertEqual(b, "is integer")
        self.assertEqual(c, None)

    def test_match_on_predicate_in_iterable_key(self):
        value = 7
        with switch(value) as s:
            a = s.case(('foo', lambda n: n < 10, lambda n: False), lambda: "bar")

        self.assertEqual(a, "bar")

    def test_dictionary_key_raises_value_error(self):
        with self.assertRaises(ValueError):
            with switch(7) as s:
                s.case({'hello': 'world'}, lambda: True)