import asyncio

from aiogram import html, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, CallbackQuery, Message

from enums.logs import Logs
from enums.markups import Markups
from enums.strings import Messages, Alerts
from loggers.setup import LOGGER


async def try_send_msg_with_effect(
    bot: Bot,
    chat_id: int | str,
    text: str,
    reply_markup: InlineKeyboardMarkup,
    message_effect_id: str,
    disable_notification: bool = True,
) -> Message:

    try:
        return await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            message_effect_id=message_effect_id,
            disable_notification=disable_notification,
        )
    except TelegramBadRequest:
        LOGGER.warning(Logs.COULDNT_SEND_MSG_WITH_EFFECT % message_effect_id)
        return await bot.send_message(
            chat_id=chat_id,
            text=text + Messages.INVALID_EFFECT_ID % html.code(message_effect_id),
            reply_markup=reply_markup,
            message_effect_id=None,
            disable_notification=disable_notification,
        )


async def delete_msg_handler(
        callback_query: CallbackQuery,
        chat_id: int | str = None,
        message_id: int = None,
) -> None:
    if not chat_id or not message_id:
        chat_id = callback_query.message.chat.id
        message_id = callback_query.message.message_id
    if (_bot := callback_query.bot) is None:
        _bot = callback_query.message.bot
    try:
        await _bot.delete_message(chat_id=chat_id, message_id=message_id)
    except TelegramBadRequest as e:
        await _bot.send_message(
            chat_id=chat_id,
            text=Messages.COULDNT_DELETE_MSG % html.code(str(message_id))
            + f"\n\n{html.code('[' + e.message + ' | (' + str(chat_id) + ';' + str(message_id) + ')]')}",
            reply_markup=Markups.ONLY_DELETE_MARKUP.value,
        )
        LOGGER.warning(Logs.COULDN_DELETE_MSG % (message_id, chat_id))


async def sleep_for_alert(
        counter: int,
        bot: Bot,
        chat_id: int | str
) -> None:
    if counter % 10 != 0:
        return

    await asyncio.sleep(2)
    await bot.send_message(
        chat_id=chat_id,
        text=Alerts.HEAL_ALERT,
        reply_markup=Markups.ONLY_DELETE_MARKUP.value,
        disable_notification=False
    )
