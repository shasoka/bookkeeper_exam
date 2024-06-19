import asyncio
import random
from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware, html
from aiogram.types import TelegramObject

from resources.strings import SUCCESS_EFFECT_IDS
from services.entities_service import get_user, changelog_seen


class ChangeLogMiddleware(BaseMiddleware):
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
                await event.answer(
                    f"""
                    {html.code('[UPDATE CHANGELOG 20.06.2024]')}
                    \nДля тебя ничего не изменилось, но изнутри я заметно похорошел 💅
                    \n\n⚠️ Послание для тех, кто не пользовался мной несколько дней: Телеграм не даст удалить мне некоторые ваши старые сообщения, поэтому, если получите сообщение об ошибке ❌🧹, воспользуйтесь командой /heal. 
                    \n\nКак обычно, если что-то сломается, пиши @shasoka
                    \nМожешь спокойно удалять это сообщение 🫥
                    \nУспехов! 🤞
                    """,
                    disable_notification=False,
                    message_effect_id=random.choice(SUCCESS_EFFECT_IDS),
                )
                await changelog_seen(str(event.from_user.id))
                await asyncio.sleep(5)
        return await handler(event, data)
