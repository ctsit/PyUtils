import unittest
import os

from py_utils import utils


class TestUtils(unittest.TestCase):
    original_file_name = 'get_unique_filename_test.file'
    first_duplicate_file_name = 'get_unique_filename_test (1).file'
    second_duplicate_file_name = 'get_unique_filename_test (2).file'

    def test_contains_html(self):
        html_markup = "<html><p></p></html>"
        non_html_text = "This is a sentence with special characters, < ? ! . '"

        self.assertEquals(True, utils._contains_html(html_markup))
        self.assertEquals(False, utils._contains_html(non_html_text))

    def test_get_unique_filename_base(self):
        self.assertEquals(utils.get_unique_filename(
            self.original_file_name), self.original_file_name)

    def test_get_unique_filename_first(self):
        open(self.original_file_name, 'w').close()
        self.assertEquals(
            utils.get_unique_filename(self.original_file_name),
            self.first_duplicate_file_name)

    def test_get_unique_filename_second(self):
        open(self.original_file_name, 'w').close()
        open(self.first_duplicate_file_name, 'w').close()
        self.assertEquals(
            utils.get_unique_filename(self.original_file_name),
            self.second_duplicate_file_name)

    def tearDown(self):
        if os.path.isfile(self.original_file_name):
            os.remove(self.original_file_name)

        if os.path.isfile(self.first_duplicate_file_name):
            os.remove(self.first_duplicate_file_name)
