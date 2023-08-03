import unittest

from py_utils import __main__


class TestMain(unittest.TestCase):
    def test_return_hello_world(self):
        expected = 'hello world'
        actual = __main__.hello_world()

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
