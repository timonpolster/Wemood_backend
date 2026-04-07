import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Konfiguriert den Root-Logger mit Console-Output und einheitlichem Format."""

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
    """Gibt einen Child-Logger unter dem 'wemood'-Namespace zurück."""
    if name:
        return logging.getLogger(f"wemood.{name}")
    return logging.getLogger("wemood")