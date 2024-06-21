from asyncio import Task
from datetime import datetime

DURATION = 1

TASKS: dict[str, (Task, datetime)] = {}
