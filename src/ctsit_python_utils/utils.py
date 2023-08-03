import smtplib
import os

from email.message import EmailMessage
from email.policy import SMTP


def send_email(sender, recipients, subject, body=None, file=None, output=None):
    """
    This script sends an email using smtp.ufl.edu. It takes arguments like Sender(required),
    Recipient(required), Attachment, Subject(required), Message.
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


def prevent_overwrite(filename):
    if not os.path.exists(filename):
        return filename

    name, extension = os.path.splitext(filename)

    count = 1

    new_filename = f'{name} ({count}){extension}'
    while os.path.exists(new_filename):
        count += 1
        new_filename = f'{name} ({count}){extension}'

    return new_filename
