import logging
import sys
from typing import Optional


def setup_logger(
    name: Optional[str] = None,
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """Setup logger with consistent formatting"""

    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )

    logger = logging.getLogger(name or __name__)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(format_string))
        logger.addHandler(handler)
        logger.setLevel(level)

    return logger