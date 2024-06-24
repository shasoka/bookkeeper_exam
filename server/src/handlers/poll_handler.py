import random

from aiogram import html
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import PollAnswer, InlineKeyboardMarkup, InlineKeyboardButton

from handlers.utility_handlers import try_send_msg_with_effect
from resources.strings import SUCCESS_STATUSES, SUCCESS_EFFECT_IDS, FAIL_STATUSES, FAIL_EFFECT_IDS
from services.entities_service import get_user_with_session, get_cur_question_with_count, append_incorrects, \
    save_msg_id, increase_progress
from services.miscellaneous import parse_answers_from_question, parse_answers_from_poll


# noinspection PyTypeChecker
async def on_poll_answer(poll_answer: PollAnswer):
    user = await get_user_with_session(str(poll_answer.user.id))
    user_session = user.session

    cur_question, questions_total = await get_cur_question_with_count(
        str(poll_answer.user.id)
    )

    answers, _ = parse_answers_from_question(cur_question.answers)
    selected_answer = parse_answers_from_poll(answers, poll_answer.option_ids)
    correct_answer = "".join(sorted(cur_question.correct_answer))

    # Удаление кнопки с подсказкой после выбора ответа
    try:
        await poll_answer.bot.edit_message_reply_markup(
            chat_id=poll_answer.user.id,
            message_id=user_session.cur_q_msg,
            reply_markup=None,
        )
    except TelegramBadRequest:
        pass

    if user_session.theme_id is not None:
        if user_session.progress < questions_total - 1:
            callback_data = "quiz"
        else:
            callback_data = "quiz_end"
    else:
        if user_session.progress < questions_total - 1:
            callback_data = "exam"
        else:
            callback_data = "exam_end"

    if selected_answer == correct_answer:
        a_msg = await try_send_msg_with_effect(
            bot=poll_answer.bot,
            chat_id=user.telegram_id,
            text="✅ " + html.bold(random.choice(SUCCESS_STATUSES)),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=(
                                "➡️"
                                if user_session.progress < questions_total - 1
                                else "🏁"
                            ),
                            callback_data=callback_data,
                        )
                    ]
                ]
            ),
            message_effect_id=random.choice(SUCCESS_EFFECT_IDS),
        )
    else:
        a_msg = await try_send_msg_with_effect(
            bot=poll_answer.bot,
            chat_id=user.telegram_id,
            text="❌ "
            + html.bold(random.choice(FAIL_STATUSES))
            + "\n\n❕ "
            + html.bold("Правильный ответ:")
            + " "
            + html.italic(correct_answer),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=(
                                "➡️"
                                if user_session.progress < questions_total - 1
                                else "🏁"
                            ),
                            callback_data=callback_data,
                        )
                    ]
                ]
            ),
            message_effect_id=random.choice(FAIL_EFFECT_IDS),
        )
        await append_incorrects(str(poll_answer.user.id), cur_question.id)

    await save_msg_id(str(poll_answer.user.id), a_msg.message_id, "a")
    await increase_progress(str(poll_answer.user.id))
