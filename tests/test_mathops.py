"""Synthetic acceptance tests; the starter implementation must FAIL some tests."""
import unittest

from mathops import safe_add


class TestSafeAdd(unittest.TestCase):
    def test_typical(self):
        self.assertEqual(safe_add(3, 4), 7)

    def test_zero(self):
        self.assertEqual(safe_add(0, 0), 0)

    def test_upper_boundary(self):
        self.assertEqual(safe_add(10000, 0), 10000)

    def test_bool_is_not_int_for_this_contract(self):
        with self.assertRaises(TypeError):
            safe_add(True, 1)
        with self.assertRaises(TypeError):
            safe_add(1, False)

    def test_non_integer_types_rejected(self):
        for value in ("3", 3.0, None, [3]):
            with self.subTest(value=repr(value)):
                with self.assertRaises(TypeError):
                    safe_add(value, 1)

    def test_negative_rejected(self):
        with self.assertRaises(ValueError):
            safe_add(-1, 1)

    def test_large_operand_rejected(self):
        with self.assertRaises(ValueError):
            safe_add(10001, 0)

    def test_sum_overflow_rejected(self):
        with self.assertRaises(ValueError):
            safe_add(8000, 3000)

    def test_exact_integer_output(self):
        value = safe_add(5, 6)
        self.assertEqual(type(value), int)
        self.assertEqual(value, 11)


if __name__ == "__main__":
    unittest.main()
