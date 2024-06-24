import random

from aiogram import html
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from handlers.utility_handlers import delete_msg_handler, try_send_msg_with_effect
from resources.reply_markups import DELETE_INLINE_BUTTON, get_hints_button
from resources.strings import SESSION_CREATING_DELAY, SESSION_CREATED, HEAL_ALERT, on_quiz_end_success, \
    on_quiz_end_fail, SUCCESS_EFFECT_IDS, NO_MORE_HINTS
from services.entities_service import increase_help_alert_counter, get_user, init_session, clear_session, rerun_session, \
    get_user_with_session, save_msg_id, get_questions_with_len_by_theme, update_themes_progress, \
    get_cur_question_with_count, get_theme_by_id, decrease_hints
from services.miscellaneous import parse_answers_from_question


# noinspection PyTypeChecker,PyAsyncCall
async def quiz(callback_query: CallbackQuery) -> None:
    telegram_id: str = str(callback_query.from_user.id)

    if callback_query.data.startswith("quiz_init"):
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
                    text=SESSION_CREATING_DELAY % "Создаю для тебя новую! 📒",
                    show_alert=False,
                    disable_notification=False,
                    cache_time=5
                )
                alive_sessions = False
            await clear_session(callback_query, callback_query.bot)

        await callback_query.answer(
            text=SESSION_CREATED,
            show_alert=False,
            disable_notification=False,
        )

        if user.help_alert_counter % 10 == 0:
            await callback_query.answer(
                text=HEAL_ALERT, show_alert=True, disable_notification=False
            )

    if callback_query.data.startswith("quiz_incorrect"):
        await delete_msg_handler(callback_query)
        await rerun_session(telegram_id)

    if callback_query.data.startswith("quiz_end"):
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
                on_quiz_end_success(user.session)
                if without_mistakes
                else on_quiz_end_fail(user.session)
            ),
            reply_markup=(
                InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🧩", callback_data="quiz_incorrect"
                            )
                        ],
                        [DELETE_INLINE_BUTTON],
                    ]
                )
                if not without_mistakes
                else InlineKeyboardMarkup(inline_keyboard=[[DELETE_INLINE_BUTTON]])
            ),
            message_effect_id=random.choice(SUCCESS_EFFECT_IDS),
        )

        _, questions_total = await get_questions_with_len_by_theme(
            user.session.theme_id
        )
        if without_mistakes:
            # Если тест пройден без ошибок, то нужно проверить ситуацию пройден ли он без исправления ошибок
            if questions_total == user.session.questions_total:
                # Если кол-во вопросов в сессии равно кол-ву вопросов в выбранной теме, вешаем "зеленый" маркер
                await update_themes_progress(
                    user.telegram_id, user.session.theme_id, without_mistakes
                )
            else:
                # Если кол-во вопросов в сессии НЕ равно кол-ву вопросов в выбранной теме, вешаем "желтый" маркер
                await update_themes_progress(
                    user.telegram_id, user.session.theme_id, not without_mistakes
                )

        await save_msg_id(user.telegram_id, s_msg.message_id, "s")
        return

    user = await get_user_with_session(telegram_id)
    if user.session.questions_total == user.session.progress:
        raise IndexError

    await save_msg_id(telegram_id, None, "a")

    cur_question, questions_total = await get_cur_question_with_count(telegram_id)
    if not callback_query.data.startswith("quiz_init") and not callback_query.data.startswith("quiz_incorrect"):
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
    theme = await get_theme_by_id(user.session.theme_id)

    if (
        user.session.theme_id
        not in user.themes_done_full + user.themes_tried + user.themes_done_particular
    ):
        await update_themes_progress(user.telegram_id, user.session.theme_id, None)

    _bot = callback_query.bot if callback_query.bot else callback_query.message.bot
    q_msg = await _bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=f"{html.code(f'{user.session.progress + 1} / {questions_total}')}\n"
             f"\n{html.code(theme.title)}\n\n{html.bold(cur_question.title)}\n\n{answers_str}",
        disable_notification=True,
        reply_markup=(
            InlineKeyboardMarkup(inline_keyboard=[[get_hints_button(user.session)]])
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
            f"🧩 Входит в ответ: {''.join(sorted(random_hints_ids))}.\n🖼 Всего в ответе: {answer_len} буквы\n{NO_MORE_HINTS}"
            if len(cur_question.correct_answer) > 1
            else f"😐 Ты че?\nТут один верный ответ. Сам разбирайся.\n🏳️ Отнимать попытки не стану, ладно."
        ),
        show_alert=True,
    )
    if len(cur_question.correct_answer) > 1:
        await decrease_hints(str(callback_query.from_user.id))

    await callback_query.message.edit_reply_markup(reply_markup=None)
