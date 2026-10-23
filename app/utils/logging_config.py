import logging


def configure_logging() -> None:
    """Set up basic application logging without sensitive request data."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
