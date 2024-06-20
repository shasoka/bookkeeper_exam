import asyncio
import random
from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import TelegramObject

from resources.strings import SUCCESS_EFFECT_IDS, CHANGELOGS, INVALID_EFFECT_ID
from services.entities_service import get_user, changelog_seen


class LastChangelogMiddleware(BaseMiddleware):
    # noinspection PyTypeChecker
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:

        if event.from_user:
            user = await get_user(str(event.from_user.id))
            if not user.checked_update:
                effect_id = random.choice(SUCCESS_EFFECT_IDS)
                try:
                    await event.answer(
                        CHANGELOGS[-1],
                        disable_notification=False,
                        message_effect_id=effect_id,
                    )
                except TelegramBadRequest:
                    await event.answer(
                        CHANGELOGS[-1] + INVALID_EFFECT_ID % html.code(effect_id),
                        disable_notification=False,
                    )
                await changelog_seen(str(event.from_user.id))
                await asyncio.sleep(5)
        return await handler(event, data)
