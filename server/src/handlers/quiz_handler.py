import asyncio
import random

from aiogram import html
from aiogram.types import CallbackQuery

from enums.logs import Logs
from enums.markups import Markups
from enums.strings import CallbackQueryAnswers, Alerts, Arrays, Messages
from handlers.utility_handlers import (
    delete_msg_handler,
    try_send_msg_with_effect,
    sleep_for_alert,
)
from loggers.setup import LOGGER
from services.entities_service import (
    increase_help_alert_counter,
    get_user,
    init_session,
    clear_session,
    rerun_session,
    get_user_with_session,
    save_msg_id,
    get_questions_with_len_by_theme,
    update_themes_progress,
    get_cur_question_with_count,
    get_theme_by_id,
    decrease_hints,
)
from services.utility_service import parse_answers_from_question


# noinspection PyTypeChecker,PyAsyncCall
async def quiz(callback_query: CallbackQuery) -> None:
    """
    Function, which handles incoming ``aiogram.types.CallbackQuery``, which ``data`` property starts with ``quiz``.

    Variants of incomig queries are:

    - ``quiz``: deletes previous question messages and sends next;
    - ``quiz_init_{chosen_theme_id}``: initializes new session and proceeds the code, which runs on ``quiz``;
    - ``quiz_init_shuffle_{chosen_theme_id}`` same as previous, but questions will be shuffled;
    - ``quiz_incorrect``: reruns session with same theme, puts incorects in queue and proceeds the code, which runs on
      ``quiz``;
    - ``quiz_heal``: restores current session, if any exists, by proceeding the code, which runs on ``quiz``;
    - ``quiz_end``: shows quiz summary and suggests to re-solve incorrects.

    :param callback_query: incoming ``aiogram.types.CallbackQuery`` object
    """

    telegram_id: str = str(callback_query.from_user.id)
    # Retrieve the bot instance. Query can be too old if it was sent from /heal command
    _bot = callback_query.bot if callback_query.bot else callback_query.message.bot

    if callback_query.data.startswith("quiz_init"):
        # Logic for quiz_init_{chosen_theme_id} and quiz_init_shuffle_{chosen_theme_id}
        await increase_help_alert_counter(telegram_id)
        await delete_msg_handler(callback_query)

        user = await get_user(telegram_id)

        alive_sessions = True
        while not await init_session(
            theme_id=int(callback_query.data.split("_")[-1]),
            telegram_id=telegram_id,
            shuffle=True if "shuffle" in callback_query.data else False,
        ):
            if alive_sessions:
                await callback_query.answer(
                    text=CallbackQueryAnswers.SESSION_CREATION_DELAY
                    % CallbackQueryAnswers.QUIZ_DELAY,
                    show_alert=False,
                    disable_notification=False,
                    cache_time=5,
                )
                alive_sessions = False
                LOGGER.warning(
                    Logs.TOO_MANY_SESSIONS % (user.telegram_id + "@" + user.username)
                )
            await clear_session(callback_query, callback_query.bot)

        await callback_query.answer(
            text=CallbackQueryAnswers.QUIZ_SESSION_CREATED,
            show_alert=False,
            disable_notification=False,
        )

        asyncio.create_task(
            sleep_for_alert(
                user.help_alert_counter, _bot, callback_query.message.chat.id
            )
        )

    if callback_query.data.startswith("quiz_incorrect"):
        # Logic for quiz_incorrect
        await delete_msg_handler(callback_query)
        await rerun_session(telegram_id)

    if callback_query.data.startswith("quiz_end"):
        # Logic for quiz_end
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

        without_mistakes = True if len(user.session.incorrect_questions) == 0 else False
        s_msg = await try_send_msg_with_effect(
            bot=callback_query.bot,
            chat_id=callback_query.message.chat.id,
            text=(
                Messages.ON_QUIZ_END_SUCCESS
                % html.code(
                    str(
                        user.session.questions_total
                        - len(user.session.incorrect_questions)
                    )
                    + "/"
                    + str(user.session.questions_total)
                )
                if without_mistakes
                else Messages.ON_QUIZ_END_FAIL
                % html.code(
                    str(
                        user.session.questions_total
                        - len(user.session.incorrect_questions)
                    )
                    + "/"
                    + str(user.session.questions_total)
                )
            ),
            reply_markup=(
                Markups.QUIZ_S_MSG_MARKUP.value
                if not without_mistakes
                else Markups.ONLY_DELETE_MARKUP.value
            ),
            message_effect_id=random.choice(Arrays.SUCCESS_EFFECT_IDS.value),
        )

        _, questions_total = await get_questions_with_len_by_theme(
            user.session.theme_id
        )
        if without_mistakes:
            # If test done without mistakes, then check if quiz_incorrect was requested
            if questions_total == user.session.questions_total:
                # If questions_total in session equals to questions_total in theme, then mark as "green"
                await update_themes_progress(
                    user.telegram_id, user.session.theme_id, without_mistakes
                )
            else:
                # If questions_total in session doesn't equal to questions_total in theme, then mark as "yellow"
                await update_themes_progress(
                    user.telegram_id, user.session.theme_id, not without_mistakes
                )

        await save_msg_id(user.telegram_id, s_msg.message_id, "s")
        return

    # Logic for quiz, also runs on quiz_init_* and quiz_incorrect
    user = await get_user_with_session(telegram_id)

    if user.session.questions_total == user.session.progress:
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

    await save_msg_id(telegram_id, None, "a")

    cur_question, questions_total = await get_cur_question_with_count(telegram_id)
    if not callback_query.data.startswith(
        "quiz_init"
    ) and not callback_query.data.startswith("quiz_incorrect"):
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
    theme = await get_theme_by_id(user.session.theme_id)

    # Mark as "orange"
    if (
        user.session.theme_id
        not in user.themes_done_full + user.themes_tried + user.themes_done_particular
    ):
        await update_themes_progress(user.telegram_id, user.session.theme_id, None)

    q_msg = await _bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=f"{html.code(f'{user.session.progress + 1} / {questions_total}')}\n"
        f"\n{html.code(theme.title)}\n\n{html.bold(cur_question.title)}\n\n{answers_str}",
        disable_notification=True,
        reply_markup=(
            Markups.only_hints_markup(user.session)
            if user.session.hints > 0 and user.hints_allowed
            else None
        ),
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


async def hint_requested(callback_query: CallbackQuery) -> None:
    """
    Function, which sends alert with hint to user, who asked for it.

    :param callback_query: incoming ``aiogram.types.CallbackQuery`` object
    """

    cur_question, _ = await get_cur_question_with_count(
        str(callback_query.from_user.id)
    )

    answer_len = len(cur_question.correct_answer)
    hints_will_be_given = answer_len // 2
    random_hints_ids = random.sample(
        cur_question.correct_answer.upper(), hints_will_be_given
    )
    await callback_query.answer(
        text=(
            f"🧩 Входит в ответ: {''.join(sorted(random_hints_ids))}."
            f"\n🖼 Всего в ответе: {answer_len} буквы\n{Alerts.NO_MORE_HINTS}"
            if len(cur_question.correct_answer) > 1
            else f"😐 Ты че?\nТут один верный ответ. Сам разбирайся.\n🏳️ Отнимать попытки не стану, ладно."
        ),
        show_alert=True,
    )
    if len(cur_question.correct_answer) > 1:
        await decrease_hints(str(callback_query.from_user.id))

    await callback_query.message.edit_reply_markup(reply_markup=None)
