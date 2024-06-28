"""Module for logging middleware."""

from time import time
from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, PollAnswer

from enums.logs import Logs
from loggers.setup import LOGGER
from middlewares.miscellaneous import collect_username
from services.entities_service import get_user


class LoggingMiddleware(BaseMiddleware):
    """Logging middleware-class extended from ``aiogram.BaseMiddleware``."""

    # Events counter
    __AVG_TIME_COUNTER = 0

    # List of timings, resets each 25 requests
    # Used to calcu;at eaverage timing
    __TIMINGS_LIST = []

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery | PollAnswer,
        data: dict[str, Any],
    ) -> Any:
        """
        Overrided function ``__call__`` from parent class.

        Spawns logs for each incoming authorized or not event. Log strings are based on event type.

        Each 25 events this middleware calculates aberage response time.

        :param handler: handler, which will be called after middleware function
        :param event: incoming event, basically ``aiogram.Message``, ``aiogram.CallbackQuery`` or ``aiogram.PollAnswer``
        :param data: incoming event data
        :return: ``Any``
        """

        ts = time()
        await handler(event, data)
        te = time()

        if (timing := round(te - ts, 5)) >= 5:
            timing = round(timing - 5, 5)
        LoggingMiddleware.__AVG_TIME_COUNTER += 1
        LoggingMiddleware.__TIMINGS_LIST.append(timing)

        if LoggingMiddleware.__AVG_TIME_COUNTER % 25 == 0:
            LOGGER.info(Logs.AVG_TIMING % (sum(LoggingMiddleware.__TIMINGS_LIST) / 25))
            LoggingMiddleware.__AVG_TIME_COUNTER = 0
            LoggingMiddleware.__TIMINGS_LIST = []

        telegram_id = "<unknown_id>"
        msg = f"[{Logs.LOCK}] Unknown event from @anonymous in {te - ts}"
        if isinstance(event, Message):
            username = collect_username(event, "m")
            telegram_id = event.from_user.id
            if event.text:
                if "/" in event.text:
                    msg = f'[%s{Logs.COMMAND}] Command "{event.text}" from {event.from_user.id}@{username} in {timing}'
                else:
                    msg = f'[%s{Logs.MESSAGE}] Message "{event.text}" from {event.from_user.id}@{username} in {timing}'
            else:
                msg = f'[%s{Logs.MESSAGE}] Message "<non_text_data>" from {event.from_user.id}@{username} in {timing}'
        elif isinstance(event, CallbackQuery):
            username = collect_username(event, "q")
            telegram_id = event.from_user.id
            msg = f'[%s{Logs.CALLBACK}] Callback "{event.data}" from {event.from_user.id}@{username} in {timing}'
        elif isinstance(event, PollAnswer):
            username = collect_username(event, "p")
            telegram_id = event.user.id
            answer = "".join(["абвгдежзиклмн"[i] for i in event.option_ids])
            msg = f'[%s{Logs.ANSWER}] Answer "{answer}" from {event.user.id}@{username} in {timing}'

        user = await get_user(str(telegram_id))
        if not user:
            LOGGER.info(msg % Logs.LOCK)
        else:
            LOGGER.info(msg % Logs.UNLOCK)
