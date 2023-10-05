from email.message import EmailMessage
from email.policy import SMTP

import os
import re
import smtplib


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

    pattern = r"<[^>]*>"

    if re.search(pattern, body) is not None:
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
