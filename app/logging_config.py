import logging
import os


def configure_logging() -> None:
    level = logging.DEBUG if os.getenv(
        "DEBUG",
        "false",
    ).lower() == "true" else logging.INFO

    logging.basicConfig(
        level=level,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
    )