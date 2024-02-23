import sqlite3
import unittest
import os

from py_utils import utils
from py_utils.orm import DbClient


class TestUtils(unittest.TestCase):
    test_db = "tests/db.sqlite"
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

    def test_script_helper_signature(self):
        """
        This test checks if log_failed_job and log_successful_job log status of data
        correctly. This calls the functions and saves it to local .sqlite file and checks
        if everything is inserted into the db correctly.
        """
        db_client = DbClient(f"sqlite:///{self.test_db}")
        script_helper = utils.ScriptHelper("test_signature.py", db_client)
        script_helper.log_failed_job({"info": "Could not write into sheet"}, "File not found")
        script_helper.log_successful_job({"info": "File written"})

        conn = sqlite3.connect(self.test_db)
        cur = conn.cursor()

        count_job_status_data = 0
        for i, row in enumerate(cur.execute("SELECT * FROM job_status")):
            count_job_status_data += 1
            self.assertEqual(row[5], "test_signature.py")
            self.assertIsInstance(row[9], int)
            self.assertNotEqual(len(row[10]), 0)
            if i == 0:
                self.assertEqual(row[11], 'ERROR')
            elif i == 1:
                self.assertEqual(row[11], 'INFO')

        self.assertEqual(count_job_status_data, 2)
        conn.close()

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        if os.path.isfile(self.original_file_name):
            os.remove(self.original_file_name)

        if os.path.isfile(self.first_duplicate_file_name):
            os.remove(self.first_duplicate_file_name)
