import unittest

from switchlang import closed_range, switch


# here is a custom type we can use as a key for our tests
class TestKeyObject:
    pass


class CoreTests(unittest.TestCase):
    def test_has_matched_case_int(self):
        value = 7
        with switch(value) as s:
            s.case(1, lambda: 'one')
            s.case(5, lambda: 'five')
            s.case(7, lambda: 'seven')
            s.default(lambda: 'default')

        self.assertEqual(s.result, 'seven')

    def test_has_matched_case_object(self):
        t1 = TestKeyObject()
        t2 = TestKeyObject()
        t3 = TestKeyObject()

        with switch(t2) as s:
            s.case(t1, lambda: t1)
            s.case(t2, lambda: t2)
            s.case(t3, lambda: t3)
            s.default(lambda: None)

        self.assertEqual(s.result, t2)

    def test_default_passthrough(self):
        value = 11
        with switch(value) as s:
            s.case(1, lambda: '1')
            s.case(2, lambda: '2')
            s.default(lambda: 'default')

        self.assertEqual(s.result, 'default')

    def test_default_before_matching_case_runs_both(self):
        # documented quirk: ordering is not enforced, so a default registered
        # before a matching case runs as well; this is why default belongs last
        visited = []
        with switch(2) as s:
            s.default(lambda: visited.append('default') or 'default')
            s.case(2, lambda: visited.append(2) or 2)

        self.assertEqual(s.result, 2)
        self.assertEqual(visited, ['default', 2])

    def test_none_as_valid_case(self):
        with switch(None) as s:
            s.case(1, lambda: 'one')
            s.case(None, lambda: 'none')
            s.default(lambda: 'default')

        self.assertEqual(s.result, 'none')

    def test_error_no_match_no_default(self):
        with self.assertRaises(Exception):
            with switch('val') as s:
                s.case(1, lambda: None)
                s.case(2, lambda: None)

    def test_error_duplicate_case(self):
        with self.assertRaises(ValueError):
            with switch('val') as s:
                s.case(1, lambda: None)
                s.case(1, lambda: None)

    def test_error_case_action_not_callable(self):
        with self.assertRaises(ValueError):
            with switch(1) as s:
                s.case(1, None)

        with self.assertRaises(ValueError):
            with switch(1) as s:
                s.case(1, 'not callable')

    def test_exception_in_block_propagates(self):
        visited = []
        with self.assertRaises(RuntimeError):
            with switch(1) as s:
                s.case(1, lambda: visited.append(1) or 1)
                raise RuntimeError('error inside the with block')

        # the error aborts the switch: no case actions run
        self.assertEqual(visited, [])

    def test_exception_in_case_action_propagates(self):
        with self.assertRaises(ZeroDivisionError):
            with switch(1) as s:
                s.case(1, lambda: 1 / 0)

    def test_multiple_values_one_case_range(self):
        for value in range(1, 5):
            with switch(value) as s:
                s.case(range(1, 6), lambda: '1-to-5')
                s.case(range(6, 7), lambda: '6')
                s.default(lambda: 'default')

            self.assertEqual(s.result, '1-to-5')

        for value in range(6, 7):
            with switch(value) as s:
                s.case(range(1, 6), lambda: '1-to-5')
                s.case(range(6, 7), lambda: '6')
                s.default(lambda: 'default')

            self.assertEqual(s.result, '6')

        with switch(7) as s:
            s.case(range(1, 6), lambda: '1-to-5')
            s.case(range(6, 7), lambda: '6')
            s.default(lambda: 'default')

        self.assertEqual(s.result, 'default')

    def test_multiple_values_one_case_list(self):
        with switch(6) as s:
            s.case([1, 3, 5, 7], lambda: 'odd')
            s.case([0, 2, 4, 6, 8], lambda: 'even')
            s.default(lambda: 'default')

        self.assertEqual(s.result, 'even')

    def test_return_value_from_case(self):
        value = 4
        with switch(value) as s:
            s.case([1, 3, 5, 7], lambda: value + 1)
            s.case([0, 2, 4, 6, 8], lambda: value * value)
            s.default(lambda: 0)

        self.assertEqual(s.result, 16)

    # noinspection PyStatementEffect
    def test_result_inaccessible_if_hasnt_run(self):
        with self.assertRaises(Exception):
            s = switch(7)
            s.result

    def test_result_holding_always_equal_object(self):
        # a result that compares equal to everything (numpy arrays are the
        # real-world case) must not be mistaken for the no-result sentinel
        class AlwaysEqual:
            def __eq__(self, other):
                return True

            def __hash__(self):
                return 0

        obj = AlwaysEqual()
        with switch('x') as s:
            s.case('x', lambda: obj)

        self.assertIs(s.result, obj)

    def test_none_as_valid_result(self):
        # the sentinel must separate 'computed None' from 'computed nothing'
        with switch(1) as s:
            s.case(1, lambda: None)

        self.assertIsNone(s.result)

    def test_closed_range(self):
        for value in [1, 2, 3, 4, 5]:
            with switch(value) as s:
                s.case(closed_range(1, 5), lambda: '1-to-5')
                s.case(closed_range(6, 7), lambda: '6')
                s.default(lambda: 'default')

            self.assertEqual(s.result, '1-to-5')

        with switch(0) as s:
            s.case(closed_range(1, 5), lambda: '1-to-5')
            s.case(closed_range(6, 7), lambda: '6')
            s.default(lambda: 'default')

        self.assertEqual(s.result, 'default')

        with switch(6) as s:
            s.case(closed_range(1, 5), lambda: '1-to-5')
            s.case(closed_range(6, 7), lambda: '6')
            s.default(lambda: 'default')

        self.assertEqual(s.result, '6')

    def test_closed_range_with_step(self):
        self.assertEqual(list(closed_range(1, 5)), [1, 2, 3, 4, 5])
        # the range must never overshoot stop (it used to, by step - 1)
        self.assertEqual(list(closed_range(1, 6, 2)), [1, 3, 5])
        self.assertEqual(list(closed_range(1, 10, 4)), [1, 5, 9])
        # stop is included when the step lands on it exactly
        self.assertEqual(list(closed_range(1, 7, 2)), [1, 3, 5, 7])

        # 7 lies outside [1, 6], so it must hit the default case
        with switch(7) as s:
            s.case(closed_range(1, 6, 2), lambda: '1-to-6 odds')
            s.default(lambda: 'default')

        self.assertEqual(s.result, 'default')

    def test_closed_range_invalid_step(self):
        with self.assertRaises(ValueError):
            closed_range(1, 10, 0)

        with self.assertRaises(ValueError):
            closed_range(1, 10, -2)

    def test_closed_range_invalid_bounds(self):
        with self.assertRaises(ValueError):
            closed_range(5, 1)

        # start must be strictly less than stop: one-element ranges are rejected
        with self.assertRaises(ValueError):
            closed_range(3, 3)

    def test_adjacent_closed_ranges_are_duplicates(self):
        # closed_range(1, 5) and closed_range(5, 9) both contain 5: unlike
        # plain ranges, adjacent closed ranges overlap and are duplicate cases
        with self.assertRaises(ValueError):
            with switch(3) as s:
                s.case(closed_range(1, 5), lambda: 'low')
                s.case(closed_range(5, 9), lambda: 'high')

    def test_fallthrough_simple(self):
        visited = []
        value = 2
        with switch(value) as s:
            s.case(1, lambda: visited.append(1) or 1)
            s.case(2, lambda: visited.append(2) or 2, fallthrough=True)
            s.default(lambda: visited.append('default') or 'default')

        self.assertEqual(s.result, 'default')
        self.assertEqual(visited, [2, 'default'])

    def test_fallthrough_list(self):
        visited = []
        value = 5
        with switch(value) as s:
            s.case([1, 2, 3], lambda: visited.append(1) or 1)
            s.case([4, 5, 6], lambda: visited.append(4) or 4, fallthrough=True)
            s.case([7, 8, 9], lambda: visited.append(7) or 7, fallthrough=True)
            s.default(lambda: visited.append('default') or 'default')

        self.assertEqual(s.result, 'default')
        self.assertEqual(visited, [4, 7, 'default'])

    def test_fallthrough_some_list(self):
        visited = []
        value = 5
        with switch(value) as s:
            s.case([1, 2, 3], lambda: visited.append(1) or 1)
            s.case([4, 5, 6], lambda: visited.append(4) or 4, fallthrough=True)
            s.case([7, 8, 9], lambda: visited.append(7) or 7)
            s.default(lambda: visited.append('default') or 'default')

        self.assertEqual(s.result, 7)
        self.assertEqual(visited, [4, 7])

    def test_fallthrough_then_stop(self):
        visited = []
        value = 2
        with switch(value) as s:
            s.case(1, lambda: visited.append(1) or 1)
            s.case(2, lambda: visited.append(2) or 2, fallthrough=True)
            s.case(3, lambda: visited.append(3) or 3, fallthrough=True)
            s.case(4, lambda: visited.append(4) or 4)
            s.case(5, lambda: visited.append(5) or 5)
            s.default(lambda: visited.append('default') or 'default')

        self.assertEqual(s.result, 4)
        self.assertEqual(visited, [2, 3, 4])

    def test_fallthrough_middle_then_stop(self):
        visited = []
        value = 3
        with switch(value) as s:
            s.case(1, lambda: visited.append(1) or 1)
            s.case(2, lambda: visited.append(2) or 2, fallthrough=True)
            s.case(3, lambda: visited.append(3) or 3, fallthrough=True)
            s.case(4, lambda: visited.append(4) or 4)
            s.case(5, lambda: visited.append(5) or 5)
            s.default(lambda: visited.append('default') or 'default')

        self.assertEqual(s.result, 4)
        self.assertEqual(visited, [3, 4])

    def test_fallthrough_available_but_not_hit(self):
        visited = []
        value = 5
        with switch(value) as s:
            s.case(1, lambda: visited.append(1) or 1)
            s.case(2, lambda: visited.append(2) or 2, fallthrough=True)
            s.case(3, lambda: visited.append(3) or 3, fallthrough=True)
            s.case(4, lambda: visited.append(4) or 4)
            s.case(5, lambda: visited.append(5) or 5)
            s.default(lambda: visited.append('default') or 'default')

        self.assertEqual(s.result, 5)
        self.assertEqual(visited, [5])

    def test_fallthrough__no_match_but_not_hit(self):
        visited = []
        value = 'gone'
        with switch(value) as s:
            s.case(1, lambda: visited.append(1) or 1)
            s.case(2, lambda: visited.append(2) or 2, fallthrough=True)
            s.case(3, lambda: visited.append(3) or 3, fallthrough=True)
            s.case(4, lambda: visited.append(4) or 4)
            s.case(5, lambda: visited.append(5) or 5)
            s.default(lambda: visited.append('default') or 'default')

        self.assertEqual(s.result, 'default')
        self.assertEqual(visited, ['default'])

    def test_empty_collection_clause_is_error(self):
        with self.assertRaises(ValueError):
            with switch('val') as s:
                s.case([], lambda: None)
                s.default(lambda: 'default')


if __name__ == '__main__':
    unittest.main()
