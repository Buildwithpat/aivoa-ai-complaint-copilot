import logging

from app.config import settings


def configure_logging() -> None:
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Keep third-party libraries at a coarser level so app logs stay readable.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
