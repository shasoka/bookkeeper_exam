import asyncio
import logging
import random
import sys
from typing import Annotated

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    PollAnswer, )
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from aiogram3_di import setup_di, Depends
from config import TG_TOKEN as TOKEN
from database.connection import get_async_session
from database.models import User, UserSession, Question
from middleware.auth_mw import AuthMiddleware
from resources.buttons import DELETE_INLINE_BUTTON
from resources.strings import (
    SUCCESS_STATUSES,
    FAIL_STATUSES,
    SUCCESS_EFFECT_IDS,
    FAIL_EFFECT_IDS, on_start_msg, RESTART_COMMAND, PET_ME, SECTIONS_FROM_RESTART, SECTIONS_FROM_START,
    on_section_chosen, FORWARD, BACK, BACK_TO_SECTIONS, BACK_TO_THEMES, LETS_GO, on_theme_chosen, on_quiz_end_success,
    on_quiz_end_fail, LETS_SHUFFLE, HINT, NO_MORE_HINTS,
)
from services.service import (
    get_questions_with_len_by_theme,
    get_cur_question_with_count,
    get_sections,
    get_themes_by_section,
    get_theme_by_id,
    clear_session,
    init_session,
    get_user_with_session,
    save_msg_id,
    rerun_session, decrease_hints
)


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


# noinspection PyTypeChecker
async def pet_me_button_pressed(callback_query: CallbackQuery | Message) -> None:
    sections = await get_sections()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{sections[0].title}", callback_data="section_1")],
            [InlineKeyboardButton(text=f"{sections[1].title}", callback_data="section_2")],
            [InlineKeyboardButton(text=f"{sections[2].title}", callback_data="section_3")],
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
    start_page = 1 if callback_query.data.startswith("section") else int(callback_query.data[-3])
    per_page = 5
    start_index = (start_page - 1) * per_page
    end_index = start_page * per_page
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    last_page = False

    # Добавление кнопок тем
    for i, theme in enumerate(themes[start_index:end_index]):
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=theme.title,
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
    keyboard.inline_keyboard.append([InlineKeyboardButton(text=BACK_TO_SECTIONS, callback_data="pet")])
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
    chosen_theme_from_callback, choosen_section = callback_query.data.split('_')[1:]
    chosen_theme = await get_theme_by_id(int(chosen_theme_from_callback))

    _, questions_total = await get_questions_with_len_by_theme(int(chosen_theme_from_callback))

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=BACK_TO_THEMES, callback_data="section_" + choosen_section),
                InlineKeyboardButton(text=LETS_GO, callback_data="quiz_init_" + chosen_theme_from_callback),
            ],
            [InlineKeyboardButton(text=LETS_SHUFFLE, callback_data="quiz_init_shuffle_" + chosen_theme_from_callback)],
            [DELETE_INLINE_BUTTON],
        ]
    )

    await delete_msg_handler(callback_query)
    await callback_query.message.answer(
        on_theme_chosen(chosen_theme.title, str(questions_total)),
        reply_markup=keyboard,
        disable_notification=True,
    )


# noinspection PyTypeChecker
async def quiz_started(callback_query: CallbackQuery) -> None:
    if callback_query.data.startswith("quiz_init"):
        await init_session(
            theme_id=int(callback_query.data.split("_")[-1]),
            telegram_id=str(callback_query.from_user.id),
            shuffle=True if "shuffle" in callback_query.data else False
        )

    if callback_query.data.startswith("quiz_incorrect"):
        await rerun_session(telegram_id=str(callback_query.from_user.id))

    if callback_query.data.startswith("quiz_end"):
        user = await get_user_with_session(str(callback_query.from_user.id))
        for msg_id in [
            callback_query.message.message_id,
            user.session.cur_p_msg,
            user.session.cur_q_msg
        ]:
            await delete_msg_handler(
                callback_query,
                chat_id=callback_query.message.chat.id,
                message_id=msg_id
            )

        success = True if len(user.session.incorrect_questions) == 0 else False
        s_msg = await callback_query.message.answer(
            text=on_quiz_end_success(user.session) if success else on_quiz_end_fail(user.session),
            reply_markup=(
                InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(text="🧩", callback_data="quiz_incorrect")]]
                )
                if not success
                else None
            ),
            message_effect_id=random.choice(SUCCESS_EFFECT_IDS),
            disable_notification=True,
        )

        await save_msg_id(user.telegram_id, s_msg.message_id, "s")
        return

    cur_question, questions_total = await get_cur_question_with_count(str(callback_query.from_user.id))
    user = await get_user_with_session(str(callback_query.from_user.id))
    await delete_msg_handler(callback_query)
    if not callback_query.data.startswith("quiz_init") and not callback_query.data.startswith("quiz_incorrect"):
        await delete_msg_handler(
            callback_query,
            chat_id=callback_query.message.chat.id,
            message_id=user.session.cur_p_msg
        )
        await delete_msg_handler(
            callback_query,
            chat_id=callback_query.message.chat.id,
            message_id=user.session.cur_q_msg
        )

    answers, answers_str = get_answers_string(cur_question.answers)
    theme = await get_theme_by_id(user.session.theme_id)
    q_msg = await callback_query.message.answer(
        f"{html.code(f'{user.session.progress + 1} / {questions_total}')}\n\n{html.code(theme.title)}\n\n{html.bold(cur_question.title)}\n\n{answers_str}",
        disable_notification=True,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=HINT + f" ({user.session.hints}/{user.session.hints_total})",
                    callback_data="hint"
                )
            ]
        ])
        if user.session.hints > 0
        else None
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
        disable_notification=True
    )

    await save_msg_id(user.telegram_id, q_msg.message_id, "q")
    await save_msg_id(user.telegram_id, p_msg.message_id, "p")


async def hint_requested(callback_query: CallbackQuery) -> None:
    cur_question, _ = await get_cur_question_with_count(str(callback_query.from_user.id))
    await callback_query.answer(text=f"📗 Верный ответ: {cur_question.correct_answer.upper()}.\n{NO_MORE_HINTS}", show_alert=True)
    await decrease_hints(str(callback_query.from_user.id))

    await callback_query.message.edit_reply_markup(reply_markup=None)


# noinspection PyTypeChecker
@dp.poll_answer()
async def on_poll_answer(
    poll_answer: PollAnswer,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    user = await session.execute(
        select(User)
        .where(User.telegram_id == str(poll_answer.user.id))
        .options(selectinload(User.session))
    )
    user = user.scalar()
    user_session = user.session

    cur_question = await session.execute(
        select(Question).where(
            Question.id == user_session.questions_queue[user_session.progress]
        )
    )
    cur_question = cur_question.scalar()

    questions_total = len(user_session.questions_queue)

    answers = []
    for i, ans in enumerate(cur_question.answers):
        if ans[1] == ')':
            answers.append(ans[0].lower())
        else:
            continue
    answers.sort(key=lambda x: x[0])
    selected_answer = ""
    for i, ans in enumerate(answers):
        if i in poll_answer.option_ids:
            selected_answer += ans[0]

    correct_answer = cur_question.correct_answer

    if selected_answer == correct_answer:
        a_msg = await bot.send_message(
            user.telegram_id,
            "✅ " + html.bold(random.choice(SUCCESS_STATUSES)),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=(
                                "Далее"
                                if user_session.progress < questions_total - 1
                                else "Завершить"
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
            message_effect_id=random.choice(SUCCESS_EFFECT_IDS),
            disable_notification=True,
        )
    else:
        a_msg = await bot.send_message(
            user.telegram_id,
            "❌ "
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
                                "Далее"
                                if user_session.progress < questions_total - 1
                                else "Завершить"
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
            message_effect_id=random.choice(FAIL_EFFECT_IDS),
            disable_notification=True,
        )
        await session.execute(
            update(UserSession)
            .where(UserSession.id == user_session.id)
            .values(
                incorrect_questions=func.array_append(
                    user_session.incorrect_questions, cur_question.id
                )
            )
        )

    user_session.cur_a_msg = a_msg.message_id
    user_session.progress += 1
    await session.commit()


async def delete_msg_handler(
    callback_query: CallbackQuery,
    chat_id: int | str = None,
    message_id: int = None
):
    if not chat_id or not message_id:
        chat_id = callback_query.message.chat.id
        message_id = callback_query.message.message_id
    await bot.delete_message(chat_id=chat_id, message_id=message_id)


def get_answers_string(raw_answers: list[str]) -> tuple[list, str]:
    answers = []
    for i, ans in enumerate(raw_answers):
        cur_ans = -1
        if ans[1] == ')':
            ans.replace("\n", " ")
            answers.append(ans.lower())
            cur_ans += 1
        else:
            answers[cur_ans] += (', ' + ans.lower())
    answers.sort(key=lambda x: x[0])
    return answers, html.italic("\n\n".join(answers))


bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp.message.outer_middleware(AuthMiddleware())
dp.callback_query.register(pet_me_button_pressed, lambda c: c.data == "pet")
dp.callback_query.register(theme_button_pressed, lambda c: c.data.startswith("theme"))
dp.callback_query.register(quiz_started, lambda c: c.data.startswith("quiz"))
dp.callback_query.register(delete_msg_handler, lambda c: c.data == "delete")
dp.callback_query.register(section_button_pressed, lambda c: c.data.startswith("section") or c.data.startswith("page"))
dp.callback_query.register(hint_requested, lambda c: c.data.startswith("hint"))


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Логгер
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Инверсия зависимостей
    setup_di(dp)
    # Запуск бота
    asyncio.run(main())
