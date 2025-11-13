thonimport logging
import sys
from typing import Optional

def configure_logging(level: int = logging.INFO) -> None:
    """
    Configure root logging with a simple, informative format.

    This function is idempotent: calling it multiple times has no effect
    once handlers are attached.
    """
    root = logging.getLogger()
    if root.handlers:
        # Already configured
        return

    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)
    root.setLevel(level)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Retrieve a logger with the given name, ensuring that logging has
    been configured at least once.
    """
    if not logging.getLogger().handlers:
        configure_logging()
    return logging.getLogger(name)