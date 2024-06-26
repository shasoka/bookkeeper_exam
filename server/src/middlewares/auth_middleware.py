"""Module for auth middleware."""

from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, PollAnswer

from enums.strings import Messages
from enums.types import EVENT_TYPES
from middlewares.miscellaneous import collect_username
from services.entities_service import get_user, set_username


class AuthMiddleware(BaseMiddleware):
    """``changelog_seen`` middleware-class extended from ``aiogram.BaseMiddleware``."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """
        Overrided function ``__call__`` from parent class.

        Checks if user is authorized (basically if user exists in DB).

        :param handler: handler, which will be called after middleware function
        :param event: incoming event, basically ``aiogram.Message``, ``aiogram.CallbackQuery`` or ``aiogram.PollAnswer``
        :param data: incoming event data
        :return: ``Any``
        """

        telegram_id: str = "<unknown_id>"
        if isinstance(event, (Message, CallbackQuery)):
            telegram_id = str(event.from_user.id)
        elif isinstance(event, PollAnswer):
            telegram_id = str(event.user.id)

        if not (user := await get_user(telegram_id)):
            return await event.answer(
                Messages.NOT_AUTHORIZED,
                disable_notification=True,
            )
        else:
            if not user.username:
                username = collect_username(event, EVENT_TYPES.get(type(event), ""))
                await set_username(user.telegram_id, username)
            return await handler(event, data)
