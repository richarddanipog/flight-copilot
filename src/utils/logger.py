import logging
import sys

# silence httpx
logging.getLogger("httpx").setLevel(logging.WARNING)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,  # default level
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Create project-wide logger
logger = logging.getLogger("flight-copilot")


def get_logger(name: str = None) -> logging.Logger:
    """Get a child logger (namespaced)."""
    if name:
        return logger.getChild(name)
    return logger
