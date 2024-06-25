from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from enums.strings import Messages
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

        if event.from_user:
            if not (user := await get_user(str(event.from_user.id))):
                return await event.answer(
                    Messages.NOT_AUTHORIZED,
                    disable_notification=True,
                )
            else:
                if not user.username:
                    if event.from_user.username:
                        username = event.from_user.username
                    elif event.from_user.full_name:
                        username = transliterate(
                            event.from_user.full_name.replace(" ", "_")
                        ).lower()
                    else:
                        username = str(event.from_user.id)
                    await set_username(user.telegram_id, username)
                return await handler(event, data)
