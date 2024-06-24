from aiogram import html, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, Message, CallbackQuery

from loggers.logger import LOGGER
from resources.reply_markups import DELETE_INLINE_BUTTON
from resources.strings import INVALID_EFFECT_ID, COULDNT_DELETE_MSG


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
        return await bot.send_message(
            chat_id=chat_id,
            text=text + INVALID_EFFECT_ID % html.code(message_effect_id),
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
        # if isinstance(callback_query.message, Message):
        # Otherwise callback_query.message will be an instance of InaccessibleMessage
        await _bot.send_message(
            chat_id=chat_id,
            text=COULDNT_DELETE_MSG % html.code(str(message_id))
            + f"\n\n{html.code('[' + e.message + ' | (' + str(chat_id) + ';' + str(message_id) + ')]')}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[DELETE_INLINE_BUTTON]]
            ),
        )
        LOGGER.warning(
            "[❌🧹] Couldn't delete msg=%s in chat with user=%s",
            message_id,
            chat_id,
        )
