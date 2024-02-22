from datetime import datetime
from . import utils
from typing import List

import logging
import os
import sys


fmt = '%(asctime)s  %(levelname)-9s %(message)s [%(module)s:%(funcName)s:%(lineno)s]'
logs_dir = "logs"
todays_date = datetime.today().strftime('%Y-%m-%d')
log_filename = os.path.join(logs_dir, f"log-{todays_date}.log")


def configure_logging(handlers: List[logging.Handler] = []):
    """Configures the root logger

    Configures the root logger with default settings.

    Args:
        handlers (List[logging.Handler]): The handlers to add to the logger

    Returns:
        None
    """
    formatter = logging.Formatter(fmt)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # create stream handler
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)

    # create a file handler
    file_handler = logging.FileHandler(utils.get_unique_filename(log_filename))
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    for handler in handlers:
        logger.addHandler(handler)
