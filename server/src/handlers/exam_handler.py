import asyncio
import random
from asyncio import Task
from datetime import datetime, UTC, timedelta

from aiogram import html
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from handlers.buttons_handler import delete_msg_handler
from handlers.utility_handlers import try_send_msg_with_effect
from resources.reply_markups import DELETE_INLINE_BUTTON
from resources.strings import SESSION_CREATING_DELAY, HEAL_ALERT, on_exam_end, SUCCESS_EFFECT_IDS
from services.entities_service import increase_help_alert_counter, get_user, init_exam_session, clear_session, \
    get_user_with_session, save_msg_id, update_user_exam_best, get_cur_question_with_count
from services.miscellaneous import parse_answers_from_question

DURATION = 20

TASKS: dict[str, (Task, datetime)] = {}


# noinspection PyAsyncCall
async def exam(callback_query: CallbackQuery) -> None:
    telegram_id = str(callback_query.from_user.id)

    if callback_query.data.startswith("exam_init"):
        await increase_help_alert_counter(telegram_id)
        await delete_msg_handler(callback_query)

        user = await get_user(telegram_id)

        alive_sessions = True
        while not await init_exam_session(telegram_id):
            if alive_sessions:
                await callback_query.answer(
                    text=SESSION_CREATING_DELAY % "Запускаю таймер! ⏳",
                    show_alert=False,
                    disable_notification=False,
                )
                alive_sessions = False
            await clear_session(callback_query, callback_query.bot)

        if user.help_alert_counter % 10 == 0:
            await callback_query.answer(
                text=HEAL_ALERT, show_alert=True, disable_notification=False
            )

        end_time = datetime.now(UTC) + timedelta(minutes=DURATION)
        TASKS[telegram_id] = (
            asyncio.create_task(
                handle_exam_timeout(callback_query, telegram_id, end_time)
            ),
            end_time,
        )

    if callback_query.data.startswith("exam_end"):
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
            msg_text = on_exam_end(score > user.exam_best, score)
        else:
            msg_text = (
                html.code("[ВРЕМЯ ВЫШЛО]")
                + "\n\n"
                + on_exam_end(score > user.exam_best, score).strip()
            )
        cur_task = TASKS.pop(telegram_id)
        cur_task[0].cancel()
        s_msg = await try_send_msg_with_effect(
            bot=callback_query.bot,
            chat_id=callback_query.message.chat.id,
            text=msg_text,
            reply_markup=(
                InlineKeyboardMarkup(inline_keyboard=[[DELETE_INLINE_BUTTON]])
            ),
            message_effect_id=random.choice(SUCCESS_EFFECT_IDS),
        )

        await update_user_exam_best(telegram_id, score)
        await save_msg_id(user.telegram_id, s_msg.message_id, "s")
        return

    if telegram_id not in TASKS:
        raise KeyError

    if (TASKS[telegram_id][1] - datetime.now(UTC)).total_seconds() > 2:
        cur_question, questions_total = await get_cur_question_with_count(telegram_id)
        user = await get_user_with_session(telegram_id)

        if (user.session.progress + 1) % 5 == 0:
            delta = int((TASKS[telegram_id][1] - datetime.now(UTC)).total_seconds())
            minutes, seconds = divmod(delta, 60)
            await callback_query.answer(
                text=f"⌛️ {minutes:02d}:{seconds:02d}",
                show_alert=False,
                disable_notification=True,
            )

        if not callback_query.data.startswith("exam_init"):
            to_delete = [
                user.session.cur_a_msg,
                user.session.cur_p_msg,
                user.session.cur_q_msg
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

        _bot = callback_query.bot if callback_query.bot else callback_query.message.bot
        q_msg = await _bot.send_message(
            chat_id=callback_query.message.chat.id,
            text=f"{html.code(f'{user.session.progress + 1} / {questions_total}')}"
                 f"\n{html.code(f'Раздел {"I" * cur_question.theme.section_id} | {cur_question.theme.title.split(".")[0]}')}"
                 f"\n\n{html.code('Это экзамен, братуха 🥶')}\n\n{html.bold(cur_question.title)}\n\n{answers_str}",
            disable_notification=True,
        )

        p_msg = await _bot.send_poll(
            chat_id=callback_query.message.chat.id,
            question=(
                f"Выбери {html.bold('верный')} ответ"
                if len(cur_question.correct_answer) == 1
                else f"Выбери {html.bold('верные')} ответы"
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
    time_remaining = (end_time - datetime.now(UTC)).total_seconds()
    await callback_query.answer(
        text="⏳ Время пошло", show_alert=False, disable_notification=True
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
