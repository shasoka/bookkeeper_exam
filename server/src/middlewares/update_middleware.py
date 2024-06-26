import asyncio
import random
from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import TelegramObject, LinkPreviewOptions, Message, CallbackQuery, PollAnswer

from enums.logs import Logs
from enums.markups import Markups
from enums.strings import Arrays, Messages
from loggers.setup import LOGGER
from services.entities_service import get_user, changelog_seen


class LastChangelogMiddleware(BaseMiddleware):
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

        user = await get_user(telegram_id)
        if not user.checked_update:
            effect_id = random.choice(Arrays.SUCCESS_EFFECT_IDS.value)
            try:
                await event.answer(
                    Arrays.CHANGELOGS.value[-1],
                    disable_notification=False,
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                    message_effect_id=effect_id,
                    reply_markup=Markups.ONLY_DELETE_MARKUP.value
                )
            except TelegramBadRequest:
                await event.answer(
                    Arrays.CHANGELOGS.value[-1] + Messages.INVALID_EFFECT_ID % html.code(effect_id),
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                    disable_notification=False,
                    reply_markup=Markups.ONLY_DELETE_MARKUP.value
                )
            LOGGER.info(Logs.CHANGE_LOG_SEEN % (user.telegram_id + '@' + user.username))
            await changelog_seen(str(event.from_user.id))
            await asyncio.sleep(5)

        return await handler(event, data)
