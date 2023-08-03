import unittest
import os

from py_utils import utils


class TestUtils(unittest.TestCase):
    original_file_name = 'prevent_overwrite_test.file'
    first_duplicate_file_name = 'prevent_overwrite_test (1).file'
    second_duplicate_file_name = 'prevent_overwrite_test (2).file'

    def test_prevent_overwrite_base(self):
        self.assertEquals(utils.prevent_overwrite(self.original_file_name), self.original_file_name)

    def test_prevent_overwrite_first(self):
        open(self.original_file_name, 'w').close()
        self.assertEquals(
            utils.prevent_overwrite(self.original_file_name),
            self.first_duplicate_file_name)

    def test_prevent_overwrite_second(self):
        open(self.original_file_name, 'w').close()
        open(self.first_duplicate_file_name, 'w').close()
        self.assertEquals(
            utils.prevent_overwrite(self.original_file_name),
            self.second_duplicate_file_name)

    def tearDown(self):
        if os.path.isfile(self.original_file_name):
            os.remove(self.original_file_name)

        if os.path.isfile(self.first_duplicate_file_name):
            os.remove(self.first_duplicate_file_name)
