import random

from aiogram import html
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import PollAnswer

from enums.logs import Logs
from enums.markups import Markups
from enums.strings import Arrays, Messages
from handlers.utility_handlers import try_send_msg_with_effect
from loggers.setup import LOGGER
from services.entities_service import (
    get_user_with_session,
    get_cur_question_with_count,
    append_incorrects,
    save_msg_id,
    increase_progress,
)
from services.utility_service import (
    parse_answers_from_question,
    parse_answers_from_poll,
)


async def on_poll_answer(poll_answer: PollAnswer) -> None:
    """
    Function, which handles poll answers. Poll options are collected from bounded with this poll question and presented
    as:

    - a
    - b
    - c
    - ...

    Handler checks user chosen ``option_ids`` if they are equal to correct variants and sends back the
    ``aiogram.tupes.Message`` with congratulations or disappointment.

    :param poll_answer: incoming ``aiogram.types.PollAnswer`` object
    """

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
            text=Messages.TICK
            + " "
            + html.bold(random.choice(Arrays.SUCCESS_STATUSES.value)),
            reply_markup=Markups.next_question_markup(
                next_q=user_session.progress < questions_total - 1,
                callback_data=callback_data,
            ),
            message_effect_id=random.choice(Arrays.SUCCESS_EFFECT_IDS.value),
        )
        LOGGER.info(Logs.CORRECT_ANS % (user.telegram_id + "@" + user.username))
    else:
        a_msg = await try_send_msg_with_effect(
            bot=poll_answer.bot,
            chat_id=user.telegram_id,
            text=Messages.CROSS
            + " "
            + html.bold(random.choice(Arrays.FAIL_STATUSES.value))
            + Messages.CORRECT_ANSWER
            + html.italic(correct_answer),
            reply_markup=Markups.next_question_markup(
                next_q=user_session.progress < questions_total - 1,
                callback_data=callback_data,
            ),
            message_effect_id=random.choice(Arrays.FAIL_EFFECT_IDS.value),
        )
        await append_incorrects(str(poll_answer.user.id), cur_question.id)
        LOGGER.info(Logs.INCORRECT_ANS % (user.telegram_id + "@" + user.username))

    await save_msg_id(str(poll_answer.user.id), a_msg.message_id, "a")
    await increase_progress(str(poll_answer.user.id))
