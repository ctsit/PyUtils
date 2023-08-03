import smtplib
import os

from email.message import EmailMessage
from email.policy import SMTP


def send_email(
        sender: str, recipients: list[str], subject: str, body: str | None = None,
        file: str | None = None, output=None):
    """Sends an email using smtp.ufl.edu.

    Args:
        sender (str): The sender of the email, i.e., the "From" field.
        recipients (list[str]): The recipients to send the emails to.
        subject (str): The subject line of the email.
        body (str | None): The body of the email.
        file (str | None): The path to the file to send as an attachment
        output:
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.set_content(body)

    if file:
        with open(file, "rb") as file_obj:
            msg.add_attachment(
                file_obj.read(), maintype="text", subtype="plain", filename=file_obj.name
            )

    if output:
        with open(output, "wb") as fp:
            fp.write(msg.as_bytes(policy=SMTP))
    else:
        with smtplib.SMTP("smtp.ufl.edu") as smtp:
            smtp.send_message(msg)


def get_unique_filename(path_to_file: str) -> str:
    """Get a unique filename.

    Checks if the file exists, and if the file exists the function returns a unique
    incremented filename. If the file doesn't exist the function returns the `path_to_file`
    that was provided. For example, if `my_file.pdf` already exists the function will return
    `my_file (1).pdf`, otherwise `my_file.pdf` is returned.

    Args:
        path_to_file (str): The path to the file to check.

    Returns:
        A unique filename.

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
