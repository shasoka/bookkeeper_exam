from asyncio import Task
from datetime import datetime

DURATION = 20

TASKS: dict[str, (Task, datetime)] = {}
