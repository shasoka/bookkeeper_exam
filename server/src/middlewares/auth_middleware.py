from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, PollAnswer

from enums.strings import Messages
from enums.types import EVENT_TYPES
from middlewares.miscellaneous import collect_username
from services.utility_service import transliterate
from services.entities_service import get_user, set_username


class AuthMiddleware(BaseMiddleware):
    # noinspection PyTypeChecker
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:

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
                username = collect_username(event, EVENT_TYPES.get(type(event), ''))
                await set_username(user.telegram_id, username)
            return await handler(event, data)
