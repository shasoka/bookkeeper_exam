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
                    {html.code('[UPDATE CHANGELOG 19.06.2024]')}
                    \n🛠 1. Меня подлатали {html.italic(html.strikethrough('снова'))} и исправили несколько багов 🪲, которые случались при обращении к функции /heal, во время моих попыток удалить некоторые сообщения, а также в ситуациях, когда новый пользователь не может получить ко мне доступ из-за отсутствия у него @имени_пользователя_в_tg.
                    \n\n📖 2. Меня вынудили перечитать методичку с тестами {html.italic(html.strikethrough('снова'))}, чтобы исправить {html.bold('два')} вопроса, в одном из которых слиплись варианты ответа {html.italic(html.spoiler('(что-то вроде "а) ...; б) ...;")'))}, а в другом отсутствовал верный ответ {html.italic(html.spoiler('(его там все еще нет, но скоро это исправится, возможно, даже с твоей помощью)'))}.
                    \n\n🆕 3. У нас пополнение! Новая {html.bold('команда')} /change_hints_policy. Теперь ты можешь выключить подсказки во всех тестах или включить их снова, даже во время теста! По умолчанию подсказки для тебя включены. Команда доступна из меню. 
                    \n\n🔄 4. Подсказки были {html.bold('переработаны')}. Теперь подсказки будут давать не полный ответ, а только один случайный вариант ответа из всех возможных {html.italic(html.spoiler('(если правильным ответом является строка "абв", то в качестве подсказки ты получишь лишь "а", "б" или "в")'))}.
                    \n\nЕсли что-то сломается, пиши @shasoka
                    \nМожешь спокойно удалять это сообщение 🫥
                    \nУспехов! 🤞
                    """,
                    disable_notification=False,
                    message_effect_id=random.choice(SUCCESS_EFFECT_IDS),
                )
                await changelog_seen(str(event.from_user.id))
                await asyncio.sleep(5)
        return await handler(event, data)
