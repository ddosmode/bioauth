import unittest
from src.cli import validate_username

class UsernameTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate_username("linux_user-1"), "linux_user-1")

    def test_traversal(self):
        for name in ("../root", "x/y", "", "a"*80, "UPPER"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate_username(name)
