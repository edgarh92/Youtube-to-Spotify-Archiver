import logging
import os


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)

    if not os.path.exists("./logs"):
        os.makedirs("./logs")

    logging_format = logging.Formatter(
        "%(asctime)s~%(levelname)s~\t%(message)s\n\t ~module:%(module)s\n\t~function:%(module)s"
    )
    stdout_formating = logging.Formatter("%(levelname)s - %(message)s")

    levels = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
    }
    logger.setLevel(levels.get(level, logging.INFO))

    file_handler = logging.FileHandler(f"./logs/{name}.log")
    file_handler.setFormatter(stdout_formating)
    file_handler.setLevel(logger.level)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(stdout_formating)
    stream_handler.setLevel(logger.level)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.DEBUG)
    return logger
