import asyncio
import random
from asyncio import Task
from datetime import datetime, UTC, timedelta

from aiogram import html
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from enums.logs import Logs
from enums.markups import Markups
from enums.strings import CallbackQueryAnswers, Arrays, Messages
from handlers.buttons_handler import delete_msg_handler
from handlers.utility_handlers import try_send_msg_with_effect, sleep_for_alert
from loggers.setup import LOGGER
from services.entities_service import (
    increase_help_alert_counter,
    get_user,
    init_exam_session,
    clear_session,
    get_user_with_session,
    save_msg_id,
    update_user_exam_best,
    get_cur_question_with_count,
)
from services.utility_service import parse_answers_from_question

# Constant for exam duration in minutes
EXAM_DURATION: float = 20.0

# Dictionary with alive exam sessions and bounded with them tasks
# Stores in RAM (unfortunately)
TASKS: dict[str, (Task, datetime)] = {}


# noinspection PyAsyncCall,PyTypeChecker
async def exam(callback_query: CallbackQuery) -> None:
    """
    Function, which handles incoming ``aiogram.types.CallbackQuery``, which ``data`` property starts with ``exam``.

    Variants of incomig queries are:

    - ``exam``: deletes previous question messages and sends next;
    - ``exam_init``: initializes new session and proceeds the code, which runs on ``exam``;
    - ``exam_heal``: restores current session, if any exists, by proceeding the code, which runs on ``exam``;
    - ``exam_end``: shows exam summary.

    :param callback_query: incoming ``aiogram.types.CallbackQuery`` object
    """
    telegram_id = str(callback_query.from_user.id)
    # Retrieve the bot instance. Query can be too old if it was sent from /heal command
    _bot = callback_query.bot if callback_query.bot else callback_query.message.bot

    if callback_query.data.startswith("exam_init"):
        # Logic for exam_init
        await increase_help_alert_counter(telegram_id)
        await delete_msg_handler(callback_query)

        user = await get_user(telegram_id)

        alive_sessions = True
        while not await init_exam_session(telegram_id):
            if alive_sessions:
                await callback_query.answer(
                    text=CallbackQueryAnswers.SESSION_CREATION_DELAY
                    % CallbackQueryAnswers.EXAM_DELAY,
                    show_alert=False,
                    disable_notification=False,
                )
                alive_sessions = False
                LOGGER.warning(
                    Logs.TOO_MANY_SESSIONS % (user.telegram_id + "@" + user.username)
                )
            await clear_session(callback_query, callback_query.bot)

        asyncio.create_task(
            sleep_for_alert(
                user.help_alert_counter, _bot, callback_query.message.chat.id
            )
        )

        # Get the end_time based on exam duration
        end_time = datetime.now(UTC) + timedelta(minutes=EXAM_DURATION)
        # Add cur exam session to tasks dictionary and start the async task for timer
        TASKS[telegram_id] = (
            asyncio.create_task(
                handle_exam_timeout(callback_query, telegram_id, end_time)
            ),
            end_time,
        )

    if callback_query.data.startswith("exam_end"):
        # Logic for exam_end
        user = await get_user_with_session(telegram_id)
        to_delete = [
            user.session.cur_a_msg,
            user.session.cur_p_msg,
            user.session.cur_q_msg,
        ]
        for i, msg in enumerate(to_delete):
            if msg is not None:
                await delete_msg_handler(
                    callback_query,
                    chat_id=callback_query.message.chat.id,
                    message_id=msg,
                )
                await save_msg_id(user.telegram_id, None, "apq"[i])

        score = user.session.progress - len(user.session.incorrect_questions)

        if "timeout" not in callback_query.data:
            msg_text = Messages.ON_EXAM_END % (
                (
                    Messages.EXAM_RECORD
                    if score > user.exam_best
                    else Messages.EXAM_NOT_RECORD
                ),
                html.code(str(score)),
            )
        else:
            msg_text = (
                Messages.TIMES_UP
                + "\n\n"
                + Messages.ON_EXAM_END
                % (
                    (
                        Messages.EXAM_RECORD
                        if score > user.exam_best
                        else Messages.EXAM_NOT_RECORD
                    ),
                    html.code(str(score)),
                )
            )
            LOGGER.info(Logs.EXAM_TIMEOUT % (user.telegram_id + "@" + user.username))
        cur_task = TASKS.pop(telegram_id)
        cur_task[0].cancel()
        s_msg = await try_send_msg_with_effect(
            bot=callback_query.bot,
            chat_id=callback_query.message.chat.id,
            text=msg_text,
            reply_markup=Markups.ONLY_DELETE_MARKUP.value,
            message_effect_id=random.choice(Arrays.SUCCESS_EFFECT_IDS.value),
        )

        await update_user_exam_best(telegram_id, score)
        await save_msg_id(user.telegram_id, s_msg.message_id, "s")
        return

    # Logic for quiz, also runs on exam_init
    user = await get_user_with_session(telegram_id)

    if telegram_id not in TASKS:
        await _bot.send_message(
            chat_id=callback_query.message.chat.id,
            text=Messages.SOMETHING_WENT_WRONG,
            reply_markup=Markups.ONLY_DELETE_MARKUP.value,
        )
        LOGGER.warning(
            Logs.SESSION_BROKEN
            % (str(user.session.id), user.telegram_id + "@" + user.username)
        )
        return

    if (TASKS[telegram_id][1] - datetime.now(UTC)).total_seconds() > 2:
        # Don't proceed user answer if it is less than 2 seconds before exam end to prevent sending next question after
        # exam end
        cur_question, questions_total = await get_cur_question_with_count(telegram_id)

        if (user.session.progress + 1) % 5 == 0:
            delta = int((TASKS[telegram_id][1] - datetime.now(UTC)).total_seconds())
            minutes, seconds = divmod(delta, 60)
            try:
                await callback_query.answer(
                    text=f"{CallbackQueryAnswers.TIMER} {minutes:02d}:{seconds:02d}",
                    show_alert=False,
                    disable_notification=True,
                )
            except (TelegramBadRequest, RuntimeError):
                pass

        if not callback_query.data.startswith("exam_init"):
            to_delete = [
                user.session.cur_a_msg,
                user.session.cur_p_msg,
                user.session.cur_q_msg,
            ]
            for i, msg in enumerate(to_delete):
                if msg is not None:
                    await delete_msg_handler(
                        callback_query,
                        chat_id=callback_query.message.chat.id,
                        message_id=msg,
                    )
                    await save_msg_id(user.telegram_id, None, "apq"[i])

        answers, answers_str = parse_answers_from_question(cur_question.answers)

        q_msg = await _bot.send_message(
            chat_id=callback_query.message.chat.id,
            text=f"{html.code(f'{user.session.progress + 1} / {questions_total}')}"
            f"\n{html.code(f'Раздел {"I" * cur_question.theme.section_id} | {cur_question.theme.title.split(".")[0]}')}"
            f"\n\n{Messages.THIS_IS_EXAM}\n\n{html.bold(cur_question.title)}\n\n{answers_str}",
            disable_notification=True,
        )

        p_msg = await _bot.send_poll(
            chat_id=callback_query.message.chat.id,
            question=(
                Messages.SELECT_ONE
                if len(cur_question.correct_answer) == 1
                else Messages.SELECT_MANY
            ),
            options=[ans.lower()[:2] for ans in answers],
            type="regular",
            allows_multiple_answers=True,
            is_anonymous=False,
            disable_notification=True,
        )

        await save_msg_id(user.telegram_id, q_msg.message_id, "q")
        await save_msg_id(user.telegram_id, p_msg.message_id, "p")


async def handle_exam_timeout(
    callback_query: CallbackQuery, telegram_id, end_time
) -> None:
    """
    Function, which is used as ``asyncio.Task``. Implements timer for exam.

    If time is up, then this function will terminate exam session by sending ``aiogram.types.CallbackQuery`` with
    ``data`` property equals to ``exam_end_timeout``.

    :param callback_query: incoming ``aiogram.types.CallbackQuery`` object
    :param telegram_id: user, who started exam session
    :param end_time: time, when exam must be stopped
    :return:
    """

    time_remaining = (end_time - datetime.now(UTC)).total_seconds()
    await callback_query.answer(
        text=CallbackQueryAnswers.EXAM_SESSION_CREATED,
        show_alert=False,
        disable_notification=True,
    )
    await asyncio.sleep(time_remaining)

    user = await get_user_with_session(telegram_id)
    user_session = user.session

    if user_session and user_session.progress < 35 and datetime.now(UTC) >= end_time:
        return await exam(
            CallbackQuery(
                id=callback_query.id,
                from_user=callback_query.from_user,
                chat_instance=callback_query.chat_instance,
                message=callback_query.message,
                data="exam_end_timeout",
            )
        )
