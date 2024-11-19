import logging
import sys
import os
from datetime import datetime


def create_logger():
    """
    Create a logger object to log messages to the console and to a file.

    :return: Logger object
    """

    logger = logging.getLogger("cosy_logger")
    if not os.path.exists("./logs"):
        os.makedirs("./logs")
    logger.setLevel(
        logging.DEBUG
    )  # create console handler and set level to debug
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    date = datetime.now()
    date_string = date.strftime("%Y-%m-%d %H-%M-%S")
    fh = logging.FileHandler(f"logs/{date_string}.log")
    fh.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger


logger = create_logger()
