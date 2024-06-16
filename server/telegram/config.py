import os

from typing import Final
from dotenv import load_dotenv

load_dotenv()

# Константы конфигурации для соединения с БД
DB_HOST: Final[str] = os.environ.get("DB_HOST")
DB_PORT: Final[str] = os.environ.get("DB_PORT")
DB_NAME: Final[str] = os.environ.get("DB_NAME")
DB_USER: Final[str] = os.environ.get("DB_USER")
DB_PASS: Final[str] = os.environ.get("DB_PASS")

# Константы конфигурации для бота
TG_TOKEN: Final[str] = os.environ.get("TG_TOKEN")
