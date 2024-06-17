from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from resources.strings import NOT_AUTHORIZED
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
                    NOT_AUTHORIZED,
                    disable_notification=True,
                )
                # return await event.answer(
                #     """
                #     Технические работы 😭
                #     """,
                #     disable_notification=True,
                # )
            else:
                if not user.username:
                    await set_username(user.telegram_id, event.from_user.username)
                return await handler(event, data)
