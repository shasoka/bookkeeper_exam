"""Module for commands handlers."""


from aiogram import html
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery

from enums.markups import Markups
from enums.strings import Messages
from handlers.buttons_handler import pet_me_button_pressed
from handlers.exam_handler import exam, TASKS
from handlers.quiz_handler import quiz
from services.entities_service import (
    clear_session,
    get_user,
    get_user_with_session,
    change_hints_policy,
)


async def command_start_handler(message: Message) -> None:
    """
    Handler for incoming ``/start`` command.

    It awaits user's session clearing (if any exists) and sends back new on-start-message with inline keyboard.

    :param message: incoming Telegram message from user
    """

    await clear_session(message, message.bot)

    await message.answer(
        Messages.ON_START_MESSAGE % html.bold(message.from_user.full_name),
        reply_markup=Markups.PET_ME_MARKUP.value,
        disable_notification=True,
    )


async def command_exam_handler(message: Message) -> None:
    """
    Handler for incoming ``/exam`` command.

    It awaits user's session clearing (if any exists) and sends back new pre-exam-message with inline keyboard.

    :param message: incoming Telegram message from user
    """

    await clear_session(message, message.bot)

    user = await get_user(str(message.from_user.id))

    await message.answer(
        text=Messages.EXAM_MESSAGE % html.code(str(user.exam_best)),
        reply_markup=Markups.FIGHT_ME_MARKUP.value,
        disable_notification=True,
    )


async def command_restart_handler(message: Message) -> None:
    """
    Handler for incoming ``/restart`` command.

    It awaits user's session clearing (if any exists) and calls back to state, where user can choose section.

    :param message: incoming Telegram message from user
    """

    # Stop async timer task if any exists
    if (telegram_id := str(message.from_user.id)) in TASKS:
        cur_task = TASKS.pop(telegram_id)
        cur_task[0].cancel()

    await clear_session(message, message.bot)
    # Imitating the same behaviour as when user pressed the "pet_me" button
    await pet_me_button_pressed(callback_query=message)


async def command_heal_handler(message: Message) -> None:
    """
    Handler for incoming ``/heal`` command.

    It tries to restore messages with question and poll based on current session progress.

    If session restoration fails function sends back error message.

    :param message: incoming Telegram message from user
    """

    try:
        user = await get_user_with_session(str(message.from_user.id))
        user_session = user.session
        if user_session.theme_id is not None:
            return await quiz(
                CallbackQuery(
                    id=str(message.message_id),
                    from_user=message.from_user,
                    chat_instance=str(message.chat.id),
                    message=message,
                    data="quiz_heal",
                )
            )
        else:
            return await exam(
                CallbackQuery(
                    id=str(message.message_id),
                    from_user=message.from_user,
                    chat_instance=str(message.chat.id),
                    message=message,
                    data="exam_heal",
                )
            )
    except (AttributeError, IndexError, KeyError):
        await message.answer(
            Messages.SOMETHING_WENT_WRONG,
            reply_markup=Markups.ONLY_DELETE_MARKUP.value,
        )


async def command_change_hints_policy_handler(
    message: Message,
) -> None:
    """
    Handler for incoming ``/change_hints_policy`` command.

    It changes hints policy for current user (switches between On/Off). Status message is sent back.

    :param message: incoming Telegram message from user
    """

    user = await get_user_with_session(str(message.from_user.id))
    user_session = user.session

    await message.answer(
        text=Messages.HINTS_OFF if user.hints_allowed else Messages.HINTS_ON,
        reply_markup=Markups.ONLY_DELETE_MARKUP.value,
    )
    await change_hints_policy(str(message.from_user.id))

    try:
        if user_session:
            if not user.hints_allowed:  # Hints allowed
                if user_session.cur_q_msg and (
                    not user_session.cur_a_msg
                    or user_session.cur_q_msg > user_session.cur_a_msg
                ):
                    await message.bot.edit_message_reply_markup(
                        chat_id=int(user.telegram_id),
                        message_id=user_session.cur_q_msg,
                        reply_markup=Markups.only_hints_markup(user_session),
                    )
            else:  # Hints not allowed
                if user_session.cur_q_msg:
                    await message.bot.edit_message_reply_markup(
                        chat_id=int(user.telegram_id),
                        message_id=user_session.cur_q_msg,
                        reply_markup=None,
                    )
    except (TelegramBadRequest, AttributeError):
        pass
