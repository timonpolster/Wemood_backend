import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO") -> logging.Logger:

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger = logging.getLogger("wemood")
    logger.setLevel(getattr(logging, level.upper()))
    logger.addHandler(console_handler)

    logger.propagate = False

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    if name:
        return logging.getLogger(f"wemood.{name}")
    return logging.getLogger("wemood")