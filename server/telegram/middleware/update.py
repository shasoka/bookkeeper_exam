import asyncio
import random
from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware, html
from aiogram.types import TelegramObject

from resources.strings import SUCCESS_EFFECT_IDS
from services.service import get_user, changelog_seen


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
            print('123')
            if not user.checked_update:
                await event.answer(
                    f"""
                    {html.code('[UPDATE CHANGELOG 17.06.2024]')}
                    \n\nЯ сходил к грумеру, теперь умею давать подсказки на вопросы! 🌀
                    \nКоличество подсказок вычисляется как {html.code('КОЛ-ВО ВОПРОСОВ / 10')} и округляется до {html.code('большего целого')} 🧮
                    \n\nА еще я научился запоминать название темы, которую ты выбрал. Думаю, так станет чуточку комфортнее 🫂
                    \n\nВо мне появилось много минорных изменений, которые ты вряд ли заметишь... Просто хочу сказать, что мой хозяин старается сделать из меня конфету 🍬
                    \n\nЕсли что-то сломается, пиши @shasoka
                    \nМожешь спокойно удалять это сообщение 🫥
                    \nУспехов! 🤞
                    """,
                    disable_notification=False,
                    message_effect_id=random.choice(SUCCESS_EFFECT_IDS)
                )
                await changelog_seen(str(event.from_user.id))
        return await handler(event, data)
