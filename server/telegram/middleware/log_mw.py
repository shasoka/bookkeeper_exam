from time import time
from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, PollAnswer

from loggers.logger import LOGGER
from services.auth_service import transliterate
from services.entities_service import get_user


class LoggingMiddleware(BaseMiddleware):
    __AVG_TIME_COUNTER = 0
    __TIMINGS_LIST = []

    @staticmethod
    def m_q_username(event: Message | CallbackQuery | PollAnswer) -> str:
        if not (username := event.from_user.username):
            username = transliterate(event.from_user.full_name.replace(' ', '_')).lower()
        return username

    @staticmethod
    def collect_username(event: Message | CallbackQuery | PollAnswer, flag: str) -> str:
        match flag:
            case 'm' | 'q':
                return LoggingMiddleware.m_q_username(event)
            case 'p':
                if not (username := event.user.username):
                    username = transliterate(event.user.full_name.replace(' ', '_')).lower()
                return username

    # noinspection PyTypeChecker
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery | PollAnswer,
        data: dict[str, Any],
    ) -> Any:

        ts = time()
        await handler(event, data)
        te = time()

        if (timing := round(te - ts, 5)) >= 5:
            timing = round(timing - 5, 5)
        LoggingMiddleware.__AVG_TIME_COUNTER += 1
        LoggingMiddleware.__TIMINGS_LIST.append(timing)

        if LoggingMiddleware.__AVG_TIME_COUNTER % 25 == 0:
            LOGGER.info(f'[⏳] Average timing for 25 last requsts: {sum(LoggingMiddleware.__TIMINGS_LIST) / 25:.5f}')
            LoggingMiddleware.__AVG_TIME_COUNTER = 0
            LoggingMiddleware.__TIMINGS_LIST = []

        telegram_id = '<unknown_id>'
        msg = f'Unknown event from %s in {te - ts}'
        if isinstance(event, Message):
            username = LoggingMiddleware.collect_username(event, 'm')
            telegram_id = event.from_user.id
            if event.text:
                if '/' in event.text:
                    msg = f'[%s] Command "{event.text}" from {event.from_user.id}@{username} in {timing}'
                else:
                    msg = f'[%s] Message "{event.text}" from {event.from_user.id}@{username} in {timing}'
            else:
                msg = f'[%s] Message "<non_text_data>" from {event.from_user.id}@{username} in {timing}'
        elif isinstance(event, CallbackQuery):
            username = LoggingMiddleware.collect_username(event, 'q')
            telegram_id = event.from_user.id
            msg = f'[%s] Callback "{event.data}" from {event.from_user.id}@{username} in {timing}'
        elif isinstance(event, PollAnswer):
            username = LoggingMiddleware.collect_username(event, 'p')
            telegram_id = event.user.id
            answer = ''.join(['абвгдежзиклмн'[i] for i in event.option_ids])
            msg = f'[%s] Answer "{answer}" from {event.user.id}@{username} in {timing}'

        user = await get_user(str(telegram_id))
        if not user:
            LOGGER.debug(msg % '🔒')
        else:
            LOGGER.debug(msg % '🔓')
