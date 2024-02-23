from datetime import datetime
from email.message import EmailMessage
from email.policy import SMTP
from .models import JobStatus, JobStatusLevels
from .orm import DbClient
from typing import Dict

import getpass
import json
import pytz
import os
import re
import smtplib
import socket


def _contains_html(content: str) -> bool:
    """Utility function that checks if the content contains html.

    Args:
        content (str): The content to test for html.

    Returns:
        bool: Returns True if the content contains html, and False otherwise.
    """
    pattern = r"<[^>]*>"

    if re.search(pattern, content) is not None:
        return True
    else:
        return False


def directory_exists(path_to_dir: str) -> bool:
    """Checks if the directory exists

    Args:
        path_to_dir (str): The path to the directory to check.

    Returns:
        True if the directory exists, false otherwise.
    """
    if os.path.exists(path_to_dir) and os.path.isdir(path_to_dir):
        return True
    else:
        return False


def get_unique_filename(path_to_file: str) -> str:
    """Get a unique filename.

    Checks if the file exists, and if the file exists the function returns a unique
    incremented filename. If the file doesn't exist the function returns the `path_to_file`
    that was provided. For example, if `my_file.pdf` already exists the function will return
    `my_file (1).pdf`, otherwise `my_file.pdf` is returned.

    Args:
        path_to_file (str): The path to the file to check.

    Returns:
        (str): A unique filename.

    Raises:
        OSError: If there is an error accessing the directory.
    """
    if not os.path.exists(path_to_file):
        return path_to_file

    name, extension = os.path.splitext(path_to_file)

    count = 1

    new_filename = f'{name} ({count}){extension}'
    while os.path.exists(new_filename):
        count += 1
        new_filename = f'{name} ({count}){extension}'

    return new_filename


def is_python_file(filename: str) -> bool:
    """Checks if the filename is a python file i.e., file.py

    Args:
        filename (str): The filename to check

    Returns:
        If True if the filename is a python file, and false otherwise
    """
    pattern = r"\.py$"

    if re.search(pattern, filename):
        return True

    return False


def send_email(
        host: str, sender: str, recipients: list[str], subject: str, body: str,
        *file: str, output=None):
    """Sends an email using smtp.ufl.edu.

    Args:
        host (str): The name of the remote host to which to connect.
        sender (str): The sender of the email, i.e., the "From" field.
        recipients (list[str]): The recipients to send the emails to.
        subject (str): The subject line of the email.
        body (str | None): The body of the email.
        *file (str): The path(s) to the file(s) to send as an attachment.
        output:

    Returns:
        None
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)

    if _contains_html(body):
        msg.set_content(body, subtype='html')
    else:
        msg.set_content(body)

    if file:
        for f in file:
            with open(f, "rb") as file_obj:
                msg.add_attachment(
                    file_obj.read(), maintype="text",
                    subtype="plain", filename=os.path.basename(f)
                )

    if output:
        with open(output, "wb") as fp:
            fp.write(msg.as_bytes(policy=SMTP))
    else:
        with smtplib.SMTP(host) as server:
            server.send_message(msg)


class ScriptHelper():
    """A helper class to log `JobStatus`.

    An instance of `ScriptHelper` should be instantiated at the beginning of a script i.e., `helper = ScriptHelper()`,
    and then used to call `log_failed_job` or `log_successful_job` when the script fails or completes. Internally,
    `ScriptHelper` automatically captures `start_time`, `end_time`, `executed_by`, and `elapsed_time`, `script_path`,
    `host`, and provides that information when attempting to log the `JobStatus`

    References:
    - The structure of `JobStatus` can be seen in `py_custodian/models.py`
    """

    def __init__(self, script_name: str, db_client: DbClient, tz: pytz.tzinfo.BaseTzInfo = pytz.utc):
        """Creates an instance of ScriptHelper defaulting the timezone to use UTC.

        Args:
            script_name (str): The name of the script that is creating an instance of this class.
            db_client (DbClient): The database client to write logs with.
            tz (pytz.tzinfo.BaseTzInfo, optional): The timezone to use for datetime fields. Defaults to pytz.utc.
        """
        self.__tz = tz
        self.__start_time = datetime.now(self.__tz)
        self.__parent_script = script_name
        self.__executed_by = getpass.getuser()

        self._db_client = db_client
        self._db_client.create_tables()

    def log_failed_job(self, summary_data: dict, error: str):
        """Attempt to log a failed `JobStatus` entry to the log database.

        Args:
            summary_data (Dict): Summary data to capture in the log entry.
        """
        job_status = self._get_job_status_of_type(summary_data, error, False)
        self._db_client.insert_data(job_status)

    def log_successful_job(self, summary_data: dict):
        """Attempt to log a successful `JobStatus` entry to the log database.

        Args:
            summary_data (Dict): Summary data to capture in the log entry.
        """
        job_status = self._get_job_status_of_type(summary_data, "", True)
        self._db_client.insert_data(job_status)

    def _get_job_status_of_type(self, summary_data: Dict, error: str, succeeded: bool):
        level = JobStatusLevels.INFO if succeeded else JobStatusLevels.ERROR
        end_time = datetime.now(self.__tz)
        elapsed_time = int((end_time - self.__start_time).total_seconds())

        job_status = JobStatus(
            executed_by=self.__executed_by,
            host=socket.gethostname(),
            script_path=os.path.abspath(self.__parent_script),
            script_name=self.__parent_script,
            script_start_time=self.__start_time,
            script_end_time=end_time,
            elapsed_time=elapsed_time,
            job_summary_data=json.dumps({"data": json.dumps(summary_data), "error": error}),
            level=level,
        )
        return job_status
