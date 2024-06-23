import logging
import os
import sys


class CustomFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[95m",  # Magenta
        "RESET": "\033[0m",  # Reset to default color
    }
    PATH_COLOR = "\033[96m"  # Cyan for path
    MESSAGE_COLOR = "\033[97m"  # White for message

    def format(self, record):
        if "telegram" not in (parts := record.pathname.split(os.sep)):
            record.pathname = "venv"
        else:
            src_dir_id = parts.index("telegram")
            record.pathname = "/".join(parts[src_dir_id:-1])
        if record.funcName == "<module>":
            record.funcName = "root"
        record.name = record.name.split(".")[0]
        msg = super().format(record)

        path_str = (
            "..."
            + record.pathname
            + "/"
            + record.filename
            + " in "
            + record.funcName
            + ":"
            + str(record.lineno)
        )
        lvl_str = "[" + record.levelname + ":" + record.name + "]"

        lvl_color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]

        msg = msg.replace(lvl_str, f"{lvl_color}{lvl_str}{reset}")
        msg = msg.replace(path_str, f"{self.PATH_COLOR}{path_str}{reset}")
        msg = msg.replace(
            record.message, f"{self.MESSAGE_COLOR}{record.message}{reset}"
        )

        return msg


logging.getLogger('sqlalchemy').setLevel(logging.WARN)
logging.getLogger('aiohttp').setLevel(logging.WARN)
logging.getLogger('aiogram').setLevel(logging.WARN)

LOGGER: logging.Logger = logging.getLogger()

formatter = CustomFormatter(
    # fmt="%(asctime)s [%(levelname)s:%(name)s] ...%(pathname)s/%(filename)s in %(funcName)s:%(lineno)s %(message)s",
    fmt="[%(levelname)s:%(name)s] ...%(pathname)s/%(filename)s in %(funcName)s:%(lineno)s %(message)s",  # For render
    datefmt="%d.%m %H:%M:%S",
)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)

LOGGER.handlers = [stream_handler]
LOGGER.setLevel(logging.DEBUG)

# --- #

# Custom colors examples
# LOGGER.info("Telegram bot started")
# LOGGER.debug("This is a debug message")
# LOGGER.info("This is an info message")
# LOGGER.warning("This is a warning message")
# LOGGER.error("This is an error message")
# LOGGER.critical("This is a critical message")
