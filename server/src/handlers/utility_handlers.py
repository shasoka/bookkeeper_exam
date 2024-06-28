"""Module with miscellaneous utility functions, which are used in different handlers."""

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
    """
    Function, that tries to send message with ``message_effect``. Returns ``aiogram.types.Message`` object. Effect will
    be applied on success, otherwise - won't.

    On fail catches ``aiogram.exceptions.TelegramBadRequest`` and returns message with info about invalid ``effect_id``.

    :param bot: ``aiogram.Bot`` object
    :param chat_id: chat id, where message will be sent
    :param text: message content
    :param reply_markup: message reply markup
    :param message_effect_id: message effect
    :param disable_notification: flag, whether notification should be disabled
    :return: ``aiogram,types.Message`` object
    """

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
) -> Message | None:
    """
    Handler for inline button, which deletes specified message. Also called when new ``UserSession`` is created or next
    ``Question`` is requested.

    On deletion fail catches ``aiogram.exceptions.TelegramBadRequest`` and returns message with info about invalid
    ``message_id``.

    :param callback_query: incoming ``aiogram.types.CallbackQuery`` object
    :param chat_id: chat id, where message will be sent
    :param message_id: unique identifier of message
    :return: ``aiogram.types.Message`` object on fail and ``None`` on success
    """

    if not chat_id or not message_id:
        chat_id = callback_query.message.chat.id
        message_id = callback_query.message.message_id
    if (_bot := callback_query.bot) is None:
        _bot = callback_query.message.bot
    try:
        await _bot.delete_message(chat_id=chat_id, message_id=message_id)
    except TelegramBadRequest as e:
        LOGGER.warning(Logs.COULDN_DELETE_MSG % (message_id, chat_id))
        return await _bot.send_message(
            chat_id=chat_id,
            text=Messages.COULDNT_DELETE_MSG % html.code(str(message_id))
            + f"\n\n{html.code('[' + e.message + ' | (' + str(chat_id) + ';' + str(message_id) + ')]')}",
            reply_markup=Markups.ONLY_DELETE_MARKUP.value,
        )


async def sleep_for_alert(counter: int, bot: Bot, chat_id: int | str) -> Message | None:
    """
    Function, that is used as async task via ``asyncio.create_task``. Sends alert message about ``/heal`` command every
    10th iteration.

    :param counter: iteration counter
    :param bot: ``aiogram.Bot`` object
    :param chat_id: chat id, where alert will be sent
    :return: ``aiogram.types.Message`` object if it is 10th iteration, otherwise ``None``
    """

    if counter % 10 != 0:
        return

    await asyncio.sleep(2)
    return await bot.send_message(
        chat_id=chat_id,
        text=Alerts.HEAL_ALERT,
        reply_markup=Markups.ONLY_DELETE_MARKUP.value,
        disable_notification=False,
    )
