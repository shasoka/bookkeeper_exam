from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from services.service import get_user


class AuthMiddleware(BaseMiddleware):
    # noinspection PyTypeChecker
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:

        if event.from_user:
            if not await get_user(str(event.from_user.id)):
                return await event.answer(
                    """
                    Плаки-плаки? 😭
                    \nБесплатный только хлеб в мышеловке, братуха
                    \nЧтобы получить доступ, пиши сюда ➡️ @shasoka
                    """,
                    disable_notification=True,
                )
                # return await event.answer(
                #     """
                #     Технические работы 😭
                #     """,
                #     disable_notification=True,
                # )
            else:
                return await handler(event, data)
