"""Application logging setup."""

import logging


def configure_logging(level: str = "INFO") -> None:
    """Configure one predictable stderr handler for the local process."""

    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"unknown log level: {level}")
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        force=True,
    )
