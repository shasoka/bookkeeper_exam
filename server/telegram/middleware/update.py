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
                    {html.code('[UPDATE CHANGELOG 18.06.2024]')}
                    \n🛠 1. Меня подлатали, даже выдали мне отдельный поток ⚡️, так что теперь я не буду ломаться во время простоя (хотя может быть ты этого и не замечал) 💤
                    \n\n📖 2. Я решил перечитать методичку с тестами, чтобы исправить {html.spoiler(html.italic('ВОТТАКИЕВОТСЛИПШИЕСЯСЛОВА') + ' 🧲')} и {html.spoiler(html.italic('ПЕРЕ-НОСЫ ПО СЛО-ВАМ') + ' ✂️')}
                    \n\n🚦 3. В меню выбора темы появились маркеры, которые показывают, с какими темами ты уже справился (🟢, {html.bold('*тема получит этот маркер, если ты прорешаешь ее на максимальный балл без исправления ошибок')}), какие пощупал, но не прошел полностью (🟠) и какие даже не начинал (🔴).
                    \n\n🖍 4. К сожалению, я не запомнил, какие темы ты уже прорешал, поэтому перед началом очередной темы у тебя есть возможность {html.bold('самостоятельно')} отметить ее пройденной.
                    \n\n💊 5. Появилась новая команда: {html.code('/heal')}. Если вдруг что-то сломается, не спеши писать {html.code('/restart')}, пребереги свою сломанную сессию, я попробую ее восстановить. Напоминание об этой команде будет появляться через каждые 10 новых сессий ({html.bold('*сессия считается новой, если была выбрана новая тема')}).
                    \n\n⚙️ 6. В моем профиле появилась ссылка на мой репозиторий 🏠. Пока что там не очень уютно для обычного пользователя, но если интересно, можешь заглянуть, посмотреть как я реализован.
                    \n\n🔀 7. В прошлом обновлении я забыл упомянуть о том, что теперь ты можешь выбирать будут ли перемешаны вопросы в тесте или нет. Но ты и так уже заметил 🙂 
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
