import asyncio
import concurrent.futures
import random

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    PollAnswer,
    Message,
)

from config import TG_TOKEN as TOKEN
from loggers.logger import LOGGER
from middleware.auth_mw import AuthMiddleware
from middleware.log_mw import LoggingMiddleware
from middleware.update_mw import LastChangelogMiddleware
from resources.reply_markups import DELETE_INLINE_BUTTON, get_hints_button
from resources.strings import (
    on_quiz_end_success,
    on_section_chosen,
    on_quiz_end_fail,
    on_theme_chosen,
    on_start_msg,
    CHANGE_HINTS_POLICY_COMMAND,
    SECTIONS_FROM_RESTART,
    SOMETHING_WENT_WRONG,
    SECTIONS_FROM_START,
    COULDNT_DELETE_MSG,
    SUCCESS_EFFECT_IDS,
    SUCCESS_STATUSES,
    BACK_TO_SECTIONS,
    FAIL_EFFECT_IDS,
    RESTART_COMMAND,
    BACK_TO_THEMES,
    NO_MORE_HINTS,
    FAIL_STATUSES,
    HEAL_COMMAND,
    LETS_SHUFFLE,
    HEAL_ALERT,
    MARK_THEME,
    HINTS_OFF,
    HINTS_ON,
    FORWARD,
    LETS_GO,
    PET_ME,
    BACK, INVALID_EFFECT_ID
)
from services.entities_service import (
    get_questions_with_len_by_theme,
    increase_help_alert_counter,
    get_cur_question_with_count,
    update_themes_progress,
    get_themes_by_section,
    get_user_with_session,
    change_hints_policy,
    increase_progress,
    append_incorrects,
    get_theme_by_id,
    decrease_hints,
    clear_session,
    rerun_session,
    get_sections,
    init_session,
    save_msg_id,
    get_user,
)
from services.quiz_service import parse_answers_from_question, parse_answers_from_poll

dp = Dispatcher()


# noinspection PyTypeChecker
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await clear_session(message, bot)

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
@dp.message(Command(RESTART_COMMAND))
async def command_restart_handler(message: Message) -> None:
    await clear_session(message, bot)
    await pet_me_button_pressed(callback_query=message)


@dp.message(Command(HEAL_COMMAND))
async def command_heal_handler(message: Message) -> None:
    try:
        return await quiz_started(
            CallbackQuery(
                id=str(message.message_id),
                from_user=message.from_user,
                chat_instance=str(message.chat.id),
                message=message,
                data="quiz_heal",
            )
        )
    except (AttributeError, IndexError):
        await message.answer(
            SOMETHING_WENT_WRONG,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[DELETE_INLINE_BUTTON]]),
        )


@dp.message(Command(CHANGE_HINTS_POLICY_COMMAND))
async def command_change_hints_policy_handler(message: Message) -> None:
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
                        not user_session.cur_a_msg or user_session.cur_q_msg > user_session.cur_a_msg
                ):
                    await bot.edit_message_reply_markup(
                        chat_id=int(user.telegram_id),
                        message_id=user_session.cur_q_msg,
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[get_hints_button(user_session)]]),
                    )
            else:  # Hints not allowed
                if user_session.cur_q_msg:
                    await bot.edit_message_reply_markup(
                        chat_id=int(user.telegram_id),
                        message_id=user_session.cur_q_msg,
                        reply_markup=None,
                    )
    except (TelegramBadRequest, AttributeError):
        pass


# noinspection PyTypeChecker
async def pet_me_button_pressed(callback_query: CallbackQuery | Message) -> None:
    sections = await get_sections()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{sections[0].title}", callback_data="section_1"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{sections[1].title}", callback_data="section_2"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{sections[2].title}", callback_data="section_3"
                )
            ],
            [DELETE_INLINE_BUTTON],
        ]
    )

    if isinstance(callback_query, CallbackQuery):
        await delete_msg_handler(callback_query)
        await callback_query.message.answer(
            SECTIONS_FROM_START,
            reply_markup=keyboard,
            disable_notification=True,
        )
    else:
        await bot.send_message(
            chat_id=callback_query.chat.id,
            text=SECTIONS_FROM_RESTART,
            reply_markup=keyboard,
            disable_notification=True,
        )


# noinspection PyTypeChecker
async def section_button_pressed(callback_query: CallbackQuery) -> None:
    chosen_section = int(callback_query.data[-1])
    themes = await get_themes_by_section(chosen_section)
    user = await get_user(str(callback_query.from_user.id))
    start_page = (
        1 if callback_query.data.startswith("section") else int(callback_query.data[-3])
    )
    per_page = 5
    start_index = (start_page - 1) * per_page
    end_index = start_page * per_page
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    last_page = False

    # Добавление кнопок тем
    for i, theme in enumerate(themes[start_index:end_index]):
        if theme.id in user.themes_done_full:
            marker = "🟢"
        elif theme.id in user.themes_done_particular:
            marker = "🟠"
        else:
            marker = "🔴"
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=marker + " " + theme.title,
                    callback_data=f"theme_{theme.id}_{str(chosen_section)}",
                )
            ]
        )

    # Добавление кнопки перехода на следующую страницу
    if len(themes) > end_index:
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=FORWARD,
                    callback_data=f"page_{start_page + 1}_{str(chosen_section)}",
                )
            ]
        )
    else:
        last_page = True

    # Добавление кнопки перехода на предыдущую страницу
    if start_page > 1:
        if last_page:
            keyboard.inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=BACK,
                        callback_data=f"page_{start_page - 1},{str(chosen_section)}",
                    )
                ]
            )
        else:
            keyboard.inline_keyboard[-1].insert(
                0,
                InlineKeyboardButton(
                    text=BACK,
                    callback_data=f"page_{start_page - 1},{str(chosen_section)}",
                ),
            )

    # Добавление кнопки возвращения к разделам
    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text=BACK_TO_SECTIONS, callback_data="pet")]
    )
    # Добавление кнопки удаления сообщения
    keyboard.inline_keyboard.append([DELETE_INLINE_BUTTON])

    await delete_msg_handler(callback_query)
    await callback_query.message.answer(
        on_section_chosen(chosen_section),
        reply_markup=keyboard,
        disable_notification=True,
    )


# noinspection PyTypeChecker
async def theme_button_pressed(callback_query: CallbackQuery) -> None:
    chosen_theme_from_callback, choosen_section = callback_query.data.split("_")[1:]
    chosen_theme = await get_theme_by_id(int(chosen_theme_from_callback))
    user = await get_user(str(callback_query.from_user.id))

    _, questions_total = await get_questions_with_len_by_theme(
        int(chosen_theme_from_callback)
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LETS_GO,
                    callback_data="quiz_init_" + chosen_theme_from_callback,
                )
            ],
            [
                InlineKeyboardButton(
                    text=LETS_SHUFFLE,
                    callback_data="quiz_init_shuffle_" + chosen_theme_from_callback,
                )
            ],
            (
                [
                    InlineKeyboardButton(
                        text=BACK_TO_THEMES, callback_data="section_" + choosen_section
                    ),
                    InlineKeyboardButton(
                        text=MARK_THEME,
                        callback_data="mark_theme_"
                        + str(chosen_theme.id)
                        + "_"
                        + str(choosen_section),
                    ),
                ]
                if chosen_theme.id not in user.themes_done_full
                else [
                    InlineKeyboardButton(
                        text=BACK_TO_THEMES + " ◀️",
                        callback_data="section_" + choosen_section,
                    )
                ]
            ),
            [DELETE_INLINE_BUTTON],
        ]
    )

    await delete_msg_handler(callback_query)
    await callback_query.message.answer(
        on_theme_chosen(chosen_theme.title, str(questions_total)),
        reply_markup=keyboard,
        disable_notification=True,
    )


async def mark_theme_as_done(callback_query: CallbackQuery) -> None:
    theme, section = callback_query.data.split("_")[2:]

    await update_themes_progress(str(callback_query.from_user.id), int(theme), True)
    await callback_query.answer("✅")

    new_markup = callback_query.message.reply_markup
    new_markup.inline_keyboard[0] = [
        InlineKeyboardButton(
            text=BACK_TO_THEMES + " ◀️", callback_data="section_" + section
        )
    ]
    await callback_query.message.edit_reply_markup(reply_markup=new_markup)


# noinspection PyTypeChecker
async def quiz_started(callback_query: CallbackQuery) -> None:
    if callback_query.data.startswith("quiz_init"):
        await increase_help_alert_counter(str(callback_query.from_user.id))

        user = await get_user(str(callback_query.from_user.id))

        await init_session(
            theme_id=int(callback_query.data.split("_")[-1]),
            telegram_id=str(callback_query.from_user.id),
            shuffle=True if "shuffle" in callback_query.data else False,
        )

        if user.help_alert_counter % 10 == 0:
            await callback_query.answer(
                text=HEAL_ALERT, show_alert=True, disable_notification=False
            )

    if callback_query.data.startswith("quiz_incorrect"):
        await rerun_session(telegram_id=str(callback_query.from_user.id))

    if callback_query.data.startswith("quiz_end"):
        user = await get_user_with_session(str(callback_query.from_user.id))
        for msg_id in [
            callback_query.message.message_id,
            user.session.cur_p_msg,
            user.session.cur_q_msg,
        ]:
            await delete_msg_handler(
                callback_query,
                chat_id=callback_query.message.chat.id,
                message_id=msg_id,
            )

        success = True if len(user.session.incorrect_questions) == 0 else False
        s_msg = await try_send_msg_with_effect(
            chat_id=callback_query.message.chat.id,
            text=(
                on_quiz_end_success(user.session)
                if success
                else on_quiz_end_fail(user.session)
            ),
            reply_markup=(
                InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🧩", callback_data="quiz_incorrect"
                            )
                        ]
                    ]
                )
                if not success
                else None
            ),
            message_effect_id=random.choice(SUCCESS_EFFECT_IDS)
        )

        _, questions_total = await get_questions_with_len_by_theme(
            user.session.theme_id
        )
        if questions_total == user.session.questions_total:
            await update_themes_progress(
                user.telegram_id, user.session.theme_id, success
            )
        await save_msg_id(user.telegram_id, s_msg.message_id, "s")
        return

    cur_question, questions_total = await get_cur_question_with_count(
        str(callback_query.from_user.id)
    )
    user = await get_user_with_session(str(callback_query.from_user.id))
    if not callback_query.data.startswith("quiz_heal"):
        await delete_msg_handler(callback_query)
    if not callback_query.data.startswith("quiz_init") and not callback_query.data.startswith("quiz_incorrect"):
        await delete_msg_handler(
            callback_query,
            chat_id=callback_query.message.chat.id,
            message_id=user.session.cur_p_msg,
        )
        await delete_msg_handler(
            callback_query,
            chat_id=callback_query.message.chat.id,
            message_id=user.session.cur_q_msg,
        )

    answers, answers_str = parse_answers_from_question(cur_question.answers)
    theme = await get_theme_by_id(user.session.theme_id)
    q_msg = await callback_query.message.answer(
        f"{html.code(f'{user.session.progress + 1} / {questions_total}')}\n"
        f"\n{html.code(theme.title)}\n\n{html.bold(cur_question.title)}\n\n{answers_str}",
        disable_notification=True,
        reply_markup=(
            InlineKeyboardMarkup(inline_keyboard=[[get_hints_button(user.session)]])
            if user.session.hints > 0 and user.hints_allowed
            else None
        ),
    )

    p_msg = await callback_query.message.answer_poll(
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
    await callback_query.answer(
        text=f"📗 Один из правильных: {random.choice(cur_question.correct_answer).upper()}.\n{NO_MORE_HINTS}"
        if len(cur_question.correct_answer) > 1
        else f"😐 Ты че?\nТут один верный ответ. Сам разбирайся.\n🏳️ Отнимать попытки не стану, ладно.",
        show_alert=True,
    )
    if len(cur_question.correct_answer) > 1:
        await decrease_hints(str(callback_query.from_user.id))

    await callback_query.message.edit_reply_markup(reply_markup=None)


# noinspection PyTypeChecker
@dp.poll_answer()
async def on_poll_answer(
    poll_answer: PollAnswer
):
    user = await get_user_with_session(str(poll_answer.user.id))
    user_session = user.session

    cur_question, questions_total = await get_cur_question_with_count(str(poll_answer.user.id))

    answers, _ = parse_answers_from_question(cur_question.answers)
    selected_answer = parse_answers_from_poll(answers, poll_answer.option_ids)
    correct_answer = ''.join(sorted(cur_question.correct_answer))

    # Удаление кнопки с подсказкой после выбора ответа
    try:
        await bot.edit_message_reply_markup(
            chat_id=poll_answer.user.id,
            message_id=user_session.cur_q_msg,
            reply_markup=None
        )
    except TelegramBadRequest:
        pass

    if selected_answer == correct_answer:
        a_msg = await try_send_msg_with_effect(
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
                            callback_data=(
                                "quiz"
                                if user_session.progress < questions_total - 1
                                else "quiz_end"
                            ),
                        )
                    ]
                ]
            ),
            message_effect_id=random.choice(SUCCESS_EFFECT_IDS)
        )
    else:
        a_msg = await try_send_msg_with_effect(
            chat_id=user.telegram_id,
            text="❌ " + html.bold(random.choice(FAIL_STATUSES)) + "\n\n❕ "
                 + html.bold("Правильный ответ:") + " "
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
                            callback_data=(
                                "quiz"
                                if user_session.progress < questions_total - 1
                                else "quiz_end"
                            ),
                        )
                    ]
                ]
            ),
            message_effect_id=random.choice(FAIL_EFFECT_IDS)
        )
        await append_incorrects(str(poll_answer.user.id), cur_question.id)

    await save_msg_id(str(poll_answer.user.id), a_msg.message_id, "a")
    await increase_progress(str(poll_answer.user.id))


async def delete_msg_handler(
    callback_query: CallbackQuery,
    chat_id: int | str = None,
    message_id: int = None
) -> None:
    if not chat_id or not message_id:
        chat_id = callback_query.message.chat.id
        message_id = callback_query.message.message_id
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except TelegramBadRequest as e:
        await callback_query.message.answer(
            text=COULDNT_DELETE_MSG % html.code(str(message_id)) +
            f"\n\n{html.code('[' + e.message + ' | (' + str(chat_id) + ';' + str(message_id) + ')]')}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[DELETE_INLINE_BUTTON]])
        )
        LOGGER.debug("[❌🧹] Couldn't delete msg=%s in chat with user=%s", message_id, chat_id)


async def try_send_msg_with_effect(
        chat_id: int | str,
        text: str,
        reply_markup: InlineKeyboardMarkup,
        message_effect_id: str,
        disable_notification: bool = True
) -> Message:

    try:
        return await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            message_effect_id=message_effect_id,
            disable_notification=disable_notification
        )
    except TelegramBadRequest:
        return await bot.send_message(
            chat_id=chat_id,
            text=text + INVALID_EFFECT_ID % html.code(message_effect_id),
            reply_markup=reply_markup,
            message_effect_id=None,
            disable_notification=disable_notification
        )


bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

for handler in [
    dp.message,
    dp.callback_query,
    dp.poll_answer
]:
    handler.outer_middleware(LoggingMiddleware())
dp.message.outer_middleware(AuthMiddleware())
dp.message.outer_middleware(LastChangelogMiddleware())

dp.callback_query.register(pet_me_button_pressed, lambda c: c.data == "pet")
dp.callback_query.register(theme_button_pressed, lambda c: c.data.startswith("theme"))
dp.callback_query.register(quiz_started, lambda c: c.data.startswith("quiz"))
dp.callback_query.register(delete_msg_handler, lambda c: c.data == "delete")
dp.callback_query.register(section_button_pressed, lambda c: c.data.startswith("section") or c.data.startswith("page"))
dp.callback_query.register(hint_requested, lambda c: c.data.startswith("hint"))
dp.callback_query.register(mark_theme_as_done, lambda c: c.data.startswith("mark_theme_"))


async def main() -> None:
    # Run in a custom process pool to prevent IO blocking
    with concurrent.futures.ProcessPoolExecutor() as _:
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
