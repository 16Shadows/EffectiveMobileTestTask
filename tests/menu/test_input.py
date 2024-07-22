import unittest
from modules.menu.input import converter_string, converter_int, validator_string_not_empty, validator_always, validator_int_range
from typing import Self

class ConvertStringTestSuite(unittest.TestCase):
    def test_convert_string(self: Self):
        self.assertEqual('test', converter_string(' test '))

class ConvertIntTestSuite(unittest.TestCase):
    def test_convert_int_valid(self: Self):
        self.assertEqual(5, converter_int('5'))

    def test_convert_int_invalid(self: Self):
        self.assertRaises(ValueError, lambda: converter_int('5.13'))

class ValidatorStringNotEmptyTestSuite(unittest.TestCase):
    def test_empty_string(self: Self):
        self.assertFalse(validator_string_not_empty(''))

    def test_not_empty_string(self: Self):
        self.assertFalse(validator_string_not_empty('     f'))

class ValidatorAlwaysTestSuite(unittest.TestCase):
    def test_validator_always(self: Self):
        self.assertTrue(validator_always(123))

class ValidatorIntRangeTestSuite(unittest.TestCase):
    def test_validator_int_range_no_bounds(self: Self):
        self.assertTrue(validator_int_range(123441231))

    def test_validator_int_range_lower_bound_inside(self: Self):
        self.assertTrue(validator_int_range(123441231, 0))

    def test_validator_int_range_lower_bound_outside(self: Self):
        self.assertFalse(validator_int_range(-123441231, 0))

    def test_validator_int_range_upper_bound_inside(self: Self):
        self.assertTrue(validator_int_range(-123441231, None, 0))

    def test_validator_int_range_upper_bound_outside(self: Self):
        self.assertFalse(validator_int_range(123441231, None, 0))

    def test_validator_int_range_bounds_inside(self: Self):
        self.assertTrue(validator_int_range(14, 0, 25))

    def test_validator_int_range_bounds_outside(self: Self):
        self.assertFalse(validator_int_range(-123441231, 0, 15))

if __name__ == '__main__':
    unittest.main()