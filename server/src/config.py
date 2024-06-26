"""
Module, which loads environment variables from ``.env`` file and stores them in constants.

Example ``.env`` file is in the ``server`` folder
"""


import os

from typing import Final
from dotenv import load_dotenv

load_dotenv()

# Constants for Database
DB_HOST: Final[str] = os.environ.get("DB_HOST")
DB_PORT: Final[str] = os.environ.get("DB_PORT")
DB_NAME: Final[str] = os.environ.get("DB_NAME")
DB_USER: Final[str] = os.environ.get("DB_USER")
DB_PASS: Final[str] = os.environ.get("DB_PASS")

# Constants for WebApp server
WEB_SERVER_HOST: Final[str] = os.environ.get("WEB_SERVER_HOST")
WEB_SERVER_PORT: Final[int] = int(os.environ.get("WEB_SERVER_PORT"))

# Constants for Webhook
WEBHOOK_PATH: Final[str] = os.environ.get("WEBHOOK_PATH")
WEBHOOK_SECRET: Final[str] = os.environ.get("WEBHOOK_SECRET")
BASE_WEBHOOK_URL: Final[str] = os.environ.get("BASE_WEBHOOK_URL")

# Constants for Telegram
TG_TOKEN: Final[str] = os.environ.get("TG_TOKEN")
