from typing import Coroutine, Any

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import html

from handlers.buttons_handler import pet_me_button_pressed
from handlers.exam_handler import exam, TASKS
from handlers.quiz_handler import quiz
from resources.reply_markups import DELETE_INLINE_BUTTON, get_hints_button
from resources.strings import PET_ME, on_start_msg, EXAM_MESSAGE, SOMETHING_WENT_WRONG, HINTS_OFF, HINTS_ON
from services.entities_service import clear_session, get_user, get_user_with_session, change_hints_policy


# noinspection PyTypeChecker
async def command_start_handler(message: Message) -> Coroutine[Any, Any, None]:
    """
    Handler for incoming :code:`/start` command.

    It awaits user's session clearing (if any exists) and sends back new on-start-message::code:`aiogram.Message`
    with inline keyboard.

    :param message: incoming Telegram message from user
    :return: :code:`None`
    """

    # 1. Any - type of values that the coro can yield
    # 2. Any - type of values that the coro can accept
    # 3. None - type of expecting return of the coro

    await clear_session(message, message.bot)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=PET_ME, callback_data="pet")],
            [DELETE_INLINE_BUTTON],
        ]
    )

    await message.answer(
        on_start_msg(message.from_user.full_name),
        reply_markup=keyboard,
        disable_notification=True,
    )


# noinspection PyTypeChecker
async def command_exam_handler(message: Message) -> Coroutine[Any, Any, None]:
    """
    Handler for incoming :code:`/exam` command.

    It awaits user's session clearing (if any exists) and sends back new pre-exam-message::code:`aiogram.Message`
    with inline keyboard.

    :param message: incoming Telegram message from user
    :return: :code:`None`
    """

    await clear_session(message, message.bot)

    user = await get_user(str(message.from_user.id))

    await message.answer(
        # There are always 35 questions in the exam session
        text=EXAM_MESSAGE % html.code(str(user.exam_best) + "/35"),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⚔️", callback_data="exam_init")],
                [DELETE_INLINE_BUTTON],
            ]
        ),
        disable_notification=True,
    )


# noinspection PyTypeChecker
async def command_restart_handler(message: Message) -> Coroutine[Any, Any, None]:
    """
    Handler for incoming :code:`/restart` command.

    It awaits user's session clearing (if any exists) and calls back to state, where user can choose section.

    :param message: incoming Telegram message from user
    :return: :code:`None`
    """

    # Stop async timer task if any exists
    if (telegram_id := str(message.from_user.id)) in TASKS:
        cur_task = TASKS.pop(telegram_id)
        cur_task[0].cancel()

    await clear_session(message, message.bot)
    # Imitating the same behaviour as when user pressed the "pet_me" button
    await pet_me_button_pressed(callback_query=message)


# noinspection PyTypeChecker
async def command_heal_handler(message: Message) -> Coroutine[Any, Any, None]:
    """
    Handler for incoming :code:`/heal` command.

    It tries to await user's session clearing (if any exists) and sends back new heal-message::code:`aiogram.Message`
    with inline keyboard. On successful try the message

    :param message: incoming Telegram message from user
    :return: :code:`None`
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
            SOMETHING_WENT_WRONG,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[DELETE_INLINE_BUTTON]]),
        )


# noinspection PyTypeChecker
async def command_change_hints_policy_handler(message: Message) -> Coroutine[Any, Any, None]:
    user = await get_user_with_session(str(message.from_user.id))
    user_session = user.session

    await message.answer(
        HINTS_OFF if user.hints_allowed else HINTS_ON,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[DELETE_INLINE_BUTTON]]),
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
                        reply_markup=InlineKeyboardMarkup(
                            inline_keyboard=[[get_hints_button(user_session)]]
                        ),
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
