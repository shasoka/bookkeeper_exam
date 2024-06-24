import logging
import os
import re
import sys

from loggers.colors import Colors


class CustomFormatter(logging.Formatter):
    def format(self, record):
        lvl_color = Colors.LOG_LEVLES.get(record.levelname, Colors.END)
        username_color = Colors.LIGHT_BLUE
        message_color = Colors.WHITE
        path_color = Colors.CYAN
        reset = Colors.END

        lvl_str = "[" + record.levelname + ":" + record.name + "]"
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

        if "telegram" not in (parts := record.pathname.split(os.sep)):
            record.pathname = "venv"
        else:
            src_dir_id = parts.index("telegram")
            record.pathname = "/".join(parts[src_dir_id:-1])
        if record.funcName == "<module>":
            record.funcName = "root"
        record.name = record.name.split(".")[0]
        msg = super().format(record)

        msg = msg.replace(lvl_str, f"{lvl_color}{lvl_str}{reset}")
        msg = msg.replace(path_str, f"{path_color}{path_str}{reset}")
        msg = msg.replace(record.message, f"{message_color}{record.message}{reset}")

        at_pattern = re.compile(r"(@\w+)")
        msg = at_pattern.sub(f"{username_color}\\1{reset}", msg)

        return msg


logging.getLogger("sqlalchemy").setLevel(logging.WARN)
logging.getLogger("aiohttp").setLevel(logging.WARN)
logging.getLogger("aiogram").setLevel(logging.WARN)

LOGGER: logging.Logger = logging.getLogger()

formatter = CustomFormatter(
    # fmt="%(asctime)s [%(levelname)s:%(name)s] ...%(pathname)s/%(filename)s in %(funcName)s:%(lineno)s %(message)s",
    fmt="[%(levelname)s:%(name)s] ...%(pathname)s/%(filename)s in %(funcName)s:%(lineno)s %(message)s",  # For render
    datefmt="%d.%m %H:%M:%S",
)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)

LOGGER.handlers = [stream_handler]
LOGGER.setLevel(logging.INFO)

# --- #

if __name__ == "__main__":
    # Custom colors examples
    LOGGER.info("Telegram bot started")
    LOGGER.debug("This is a debug message")
    LOGGER.info("This is an info message")
    LOGGER.warning("This is a warning message")
    LOGGER.error("This is an error message")
    LOGGER.critical("This is a critical message")
